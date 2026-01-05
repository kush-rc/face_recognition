"""
Analytics dashboard for the Streamlit application.

This module provides the UI and logic for the analytics dashboard,
including various charts and data visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pandas.api.types import CategoricalDtype
import os
from config import LOG_FILE, REQUIRED_HOURS_FULL_DAY, REQUIRED_HOURS_HALF_DAY

def decimal_to_time(decimal_hours):
    """
    Convert decimal hours to hh:mm:ss format.
    """
    total_seconds = int(decimal_hours * 3600)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate_working_hours(df):
    """
    Calculate working hours and attendance status for each employee.
    """
    df = df.sort_values(['Name', 'DateTime'])
    results_list = []
    
    for (name, date), group in df.groupby(['Name', 'Date']):
        date_obj = pd.to_datetime(date).date()
        day_of_week = date_obj.strftime('%A')
        
        if day_of_week == 'Sunday':
            continue
            
        punches = group.sort_values('DateTime')
        
        working_seconds = 0
        punch_in_time = None
        first_punch_in = None
        last_punch_out = None
        
        for _, row in punches.iterrows():
            if row['Status'] == 'Punch In':
                if punch_in_time is None: 
                    punch_in_time = row['DateTime']
                    if first_punch_in is None:
                        first_punch_in = punch_in_time
            elif row['Status'] == 'Punch Out':
                if punch_in_time is not None: 
                    working_seconds += (row['DateTime'] - punch_in_time).total_seconds()
                    last_punch_out = row['DateTime']
                    punch_in_time = None 
        
        working_hours = working_seconds / 3600
        formatted_time = decimal_to_time(working_hours)
        
        if working_hours >= REQUIRED_HOURS_FULL_DAY:
            status = "Full Day"
        elif working_hours >= REQUIRED_HOURS_HALF_DAY:
            status = "Half Day"
        else:
            status = "Absent"
        
        results_list.append({
            'Name': name,
            'Date': date,
            'WorkingHours': round(working_hours, 2),
            'FormattedTime': formatted_time,
            'AttendanceStatus': status,
            'PunchIn': first_punch_in.time() if first_punch_in else None,
            'PunchOut': last_punch_out.time() if last_punch_out else None,
            'DayOfWeek': day_of_week
        })

    if not results_list:
        return pd.DataFrame(columns=['Name', 'Date', 'WorkingHours', 'FormattedTime', 'AttendanceStatus', 'PunchIn', 'PunchOut', 'DayOfWeek'])
        
    return pd.DataFrame(results_list)

def create_employee_timeline(df, employee_name, start_date, end_date):
    """
    Create timeline data for a specific employee within a specific date range.
    """
    emp_data = df[df['Name'] == employee_name].copy()
    date_range = pd.date_range(start=start_date, end=end_date)
    timeline = pd.DataFrame(index=date_range)
    
    # Join with employee data using a datetime index
    emp_data['Date'] = pd.to_datetime(emp_data['Date'])
    timeline = timeline.join(emp_data.set_index('Date')[['WorkingHours', 'FormattedTime', 'AttendanceStatus']])
    
    timeline['AttendanceStatus'] = timeline['AttendanceStatus'].fillna('Absent')
    timeline['WorkingHours'] = timeline['WorkingHours'].fillna(0)
    timeline['FormattedTime'] = timeline['FormattedTime'].fillna('00:00:00')
    timeline['DayOfWeek'] = timeline.index.day_name()
    
    return timeline

def show_analytics_dashboard():
    """
    Displays the analytics dashboard.
    """
    st.subheader("📊 Advanced Analytics Dashboard")
        
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
            df = pd.read_csv(LOG_FILE)
            df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            df["Time"] = pd.to_datetime(df["Time"], format='%H:%M:%S').dt.time
            df["HourDecimal"] = df["Time"].apply(lambda t: t.hour + t.minute/60 + t.second/3600)
            df["DayOfWeek"] = df["DateTime"].dt.day_name()
            df["Hour"] = df["DateTime"].dt.hour
            
            st.sidebar.header("Filters")
            min_date = df["Date"].min()
            max_date = df["Date"].max()
            
            date_range = st.sidebar.date_input(
                "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
            )
            
            start_date, end_date = (date_range[0], date_range[1]) if len(date_range) == 2 else (min_date, max_date)
            
            all_employees = sorted(df["Name"].unique())
            selected_employees = st.sidebar.multiselect("Employees", options=all_employees, default=all_employees)
            
            filtered_df = df[
                (df["Date"] >= start_date) & 
                (df["Date"] <= end_date) &
                (df["Name"].isin(selected_employees))
            ].sort_values("DateTime")
            
            if filtered_df.empty:
                st.warning("No attendance data found for the selected filters.")
            else:
                attendance_status = calculate_working_hours(filtered_df)
                day_order = CategoricalDtype(
                    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True
                )
                if not attendance_status.empty:
                    attendance_status['DayOfWeek'] = attendance_status['DayOfWeek'].astype(day_order)

                overview_tab, employee_tab, raw_data_tab = st.tabs(["Overview", "Employee Analysis", "Raw Data"])
                
                with overview_tab:
                    st.subheader("Attendance Status Distribution")
                    status_counts = attendance_status['AttendanceStatus'].value_counts().reset_index()
                    status_counts.columns = ['AttendanceStatus', 'Count']
                    
                    fig = px.pie(status_counts, values='Count', names='AttendanceStatus',
                                    color='AttendanceStatus',
                                    color_discrete_map={'Full Day': '#4CAF50', 'Half Day': '#FFC107', 'Absent': '#F44336'},
                                    hole=0.4)
                    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
                    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Monthly Attendance Trend")
                    monthly_data = attendance_status.copy()
                    monthly_data['Month'] = pd.to_datetime(monthly_data['Date']).dt.to_period('M').astype(str)
                    trend_data = monthly_data.groupby(['Month', 'AttendanceStatus']).size().unstack(fill_value=0)
                    
                    for status in ['Full Day', 'Half Day', 'Absent']:
                        if status not in trend_data.columns:
                            trend_data[status] = 0
                    trend_data = trend_data[['Full Day', 'Half Day', 'Absent']]

                    fig = px.line(trend_data.reset_index(), x='Month', y=['Full Day', 'Half Day', 'Absent'],
                                    color_discrete_map={'Full Day': '#4CAF50', 'Half Day': '#FFC107', 'Absent': '#F44336'},
                                    markers=True, labels={'value': 'Count', 'variable': 'Attendance Status'})
                    fig.update_layout(yaxis_title="Count", xaxis_title="Month", legend_title="Attendance Status", hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)

                with employee_tab:
                    st.subheader("Employee Performance")
                    selected_employee = st.selectbox("Select Employee", options=selected_employees, key="emp_select")
                    
                    if selected_employee:
                        emp_stats = attendance_status[attendance_status["Name"] == selected_employee]
                        
                        if not emp_stats.empty:
                            cols = st.columns(4)
                            cols[0].metric("Total Days", len(emp_stats))
                            cols[1].metric("Avg Hours/Day", f"{emp_stats['WorkingHours'].mean():.1f}")
                            cols[2].metric("Full Days", len(emp_stats[emp_stats['AttendanceStatus'] == 'Full Day']))
                            cols[3].metric("Absent Days", len(emp_stats[emp_stats['AttendanceStatus'] == 'Absent']))
                            
                            st.subheader(f"{selected_employee}'s Attendance Timeline")
                            timeline = create_employee_timeline(attendance_status, selected_employee, start_date, end_date)
                            
                            fig = px.scatter(timeline.reset_index(), x="index", y="WorkingHours", color="AttendanceStatus",
                                                hover_data=["FormattedTime", "DayOfWeek"],
                                                color_discrete_map={'Full Day': '#4CAF50', 'Half Day': '#FFC107', 'Absent': '#F44336'},
                                                labels={"index": "Date", "WorkingHours": "Hours Worked", "FormattedTime": "Time Worked", "DayOfWeek": "Day of Week"})
                            fig.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
                            fig.add_hline(y=REQUIRED_HOURS_FULL_DAY, line_dash="dash", line_color="#4CAF50", annotation_text="Full Day Threshold", annotation_position="bottom right")
                            fig.add_hline(y=REQUIRED_HOURS_HALF_DAY, line_dash="dash", line_color="#FFC107", annotation_text="Half Day Threshold", annotation_position="bottom right")
                            fig.update_layout(yaxis_range=[0, REQUIRED_HOURS_FULL_DAY + 2], showlegend=True)
                            st.plotly_chart(fig, use_container_width=True)
                            
                        else:
                            st.info(f"No records for {selected_employee} in the selected date range.")

                with raw_data_tab:
                    st.subheader("Attendance Punch Records (Filtered)")
                    display_records = filtered_df[['Name', 'Date', 'Time', 'Status', 'DayOfWeek']]
                    st.dataframe(display_records)
                    
                    st.subheader("Daily Attendance Summary (Filtered)")
                    display_summary = attendance_status[['Name', 'Date', 'PunchIn', 'PunchOut', 'FormattedTime', 'AttendanceStatus']]
                    st.dataframe(display_summary)
                    
                    st.subheader("Export Data")
                    csv = attendance_status.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Attendance Report", csv, f"attendance_report_{start_date}_to_{end_date}.csv", "text/csv")
        else:
            st.warning("No attendance records found. Please mark attendance first.")
    except Exception as e:
        st.error(f"An error occurred while loading the analytics dashboard: {str(e)}")
        st.exception(e)