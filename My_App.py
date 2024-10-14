import streamlit as st
import forallpeople as si
import io
import apps.beams as beams
import apps.load_factors as lf
import tempfile
import plotly.graph_objects as go
import apps.plots as plots
import numpy as np
import app_module

st.set_page_config(layout='wide')

st.write('# Structural Analysis under Bending')

st.sidebar.subheader("Input parameters")

tab1, tab2, tab3, tab4 = st.sidebar.tabs(['Beam properties', 'Material Properties', 'Supports and Loads', 'Analysis'])

beam_data= {}

fig_m = go.Figure()
fig_s = go.Figure()
fig_d = go.Figure()

temp_file_path = None

with tab1:
    
    beam_name = st.text_input('Beam name')

    beam_length = st.number_input("Beam lenght (mm)", value=3000)
    
    I_x = st.number_input("Ix ($mm^4$)", value=1000000)
    Sx = st.number_input("Sx ($mm^3$)", value=150000)
    
    
    beam_data['beam_name'] = beam_name
    beam_data['beam_length'] = beam_length
    beam_data['I_x'] = I_x
    
    
with tab2:
    
    E = st.number_input("Young's Modulus (MPa)", value=200000)
    Fy = st.number_input("Yield Strength (MPa)", value=150)
    
    beam_data['E'] = E
    
with tab3:

    st.subheader('Support Information')
    
    numb_of_sup = st.number_input('Amount of supports',1,10,step = 1)
    
    support_data = []
    
    for each_support in range(numb_of_sup):
        #st.sidebar.number_input(min_value = 0, max_value = beam_length)
        
        col1, col2 = st.columns([1,1])
        
        with col1:
            
            support_loc = st.number_input(f'Support-{each_support + 1} location (mm)', min_value = 0, max_value = beam_length)
            
        with col2:
            support_type = st.selectbox(f'Support-{each_support} type', ('Fixed', 'Pinned', 'Roller'))
            
        if support_type =='Fixed':
            support_code = 'F'
        elif support_type == 'Pinned':
            support_code = 'P'
        else:
            support_code = 'R'
            
        support_data.append(f'{support_loc}:{support_code}')
        
    beam_data['Supports'] = support_data
    
    
    
    st.subheader('Load Information')
    
    point_load_amount = st.number_input('Amount of point loads (inputs should be N and mm units)', 0, 10, step = 1)
    
    
    point_load_data = []
    
    for each_point_load in range(point_load_amount):
        
        col1, col2, col3 = st.columns([1,1,1])
        
        with col1:
            
            point_load_loc = st.number_input(f'P-{each_point_load + 1} loc', min_value = 0)
            
        with col2:
            
            point_load_value = st.number_input(f'P-{each_point_load + 1} value')
            
        with col3:
            load_case = st.selectbox(f'P-{each_point_load+1} case', ('D', 'L', 'S', 'W'))
            
            
        point_load_data.append(f'POINT:Fy,{point_load_value},{point_load_loc},case:{load_case}')
        
    beam_data['point_loads'] = point_load_data
    
    line_load_amount = st.number_input('Amount of line loads (inputs should be N/mm units)', 0, 10, step=1)
    
    line_load_data = []
    
    for each_line_load in range(line_load_amount):
        
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        
        with col1:
            start_loc = st.number_input(f'L-{each_line_load+1} start loc', step = 1)
            
        with col2:
            end_loc = st.number_input(f'L-{each_line_load+1} end loc', step = 1)
            
        with col3:
            line_load_value = st.number_input(f'L-{each_line_load+1} start value')
            
        with col4:
            line_load_value = st.number_input(f'L-{each_line_load+1} end value')
            
        with col5:
            line_load_case = st.selectbox(f'L-{each_line_load+1} case', ('D', 'L', 'S', 'W'))
            
        
            
        line_load_data.append(f'DIST:Fy,{line_load_value},{line_load_value},{start_loc},{end_loc},case:{line_load_case}') 
            
            
    beam_data['line_loads'] = line_load_data     
            
    
    
    
   
    
    
    if st.button('Generate Beam File'):
        
        output = io.StringIO()
        
        output.write(f'{beam_data["beam_name"]}\n')
        
        output.write(f'{beam_data["beam_length"]},{beam_data["E"]},{beam_data["I_x"]}\n')
        
        output.write(f'{support_data[0]},{support_data[1]}\n')
        
        filename = f'{beam_data["beam_name"]}_beam.txt'
        
        for load in beam_data['point_loads']:
            output.write(f'{load}\n')
            
        for line_load in beam_data['line_loads']:
            output.write(f'{line_load}\n')
                
        file_content = output.getvalue()
        output.close()
        
        st.download_button(
        label="Download Beam File",
        data=file_content,
        file_name=f"{beam_data['beam_name']}_beam.txt",
        mime="text/plain"
    )
    
                               
with tab4:
    
    uploaded_file = st.file_uploader("Upload your beam file (.txt) here", type = 'txt')
    
    if uploaded_file is not None:
        try:
            # Create a temporary file and save the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name

            # Now, pass the file path to your function
            
            st.success("Beam model loaded successfully!")
            
            
    
            
            
            
            

        except Exception as e:
            st.error(f"An error occurred: {e}")
            
            
if temp_file_path is not None:
            
    Model = beams.load_beam_model(temp_file_path, lf.ec_eurocode_combs())          
            
    Model.analyze()


    # MOMENT
                
    moment_array = Model.Members[f'{beam_name}'].moment_array('Mz', 1000, 'LC4a')
    x_m = moment_array[0]
    y_m = moment_array[1]

    y_positive_m = np.where(y_m > 0, y_m, 0)  # Positive values of y_m
    y_negative_m = np.where(y_m < 0, y_m, 0)  # Negative values of y_m



    fig_m.add_trace(
                go.Scatter(
                    x=x_m, 
                    y=[0]*len(x_m),
                    line={"color": "green"},
                    name="Beam length"
                    )
                )
                        


    # Add trace for positive moment (blue fill)
    fig_m.add_trace(
        go.Scatter(
            x=x_m, 
            y=y_positive_m * 10e-4, #kN.cm
            fill='tozeroy',  # Fill area to the x-axis
            fillcolor='rgba(0, 0, 255, 0.3)',  # Blue fill with transparency
            line=dict(color='blue'),  # Line color for positive moments
            name="Positive Moment"
        )
    )

    # Add trace for negative moment (red fill)
    fig_m.add_trace(
        go.Scatter(
            x=x_m, 
            y=y_negative_m * 10e-4, #kN.cm
            fill='tozeroy',  # Fill area to the x-axis
            fillcolor='rgba(255, 0, 0, 0.3)',  # Red fill with transparency
            line=dict(color='red'),  # Line color for negative moments
            name="Negative Moment"
        )
    )

    fig_m.update_layout(
        plot_bgcolor = 'white',  #Background color
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            tickmode='auto',  # Automatically add more tick values
            nticks=20,        # Increase number of ticks on x-axis
        ),
        yaxis=dict(
            showgrid=True,  # Show grid lines on y-axis
            gridcolor='lightgray',  # Grid line color
            gridwidth=1  # Grid line width
        )
    )


    fig_m.layout.title.text = "Moment Diagram"
    fig_m.layout.xaxis.title = "Beam Length, mm"
    fig_m.layout.yaxis.title = "Resulting Moment, kN.cm"

    st.plotly_chart(fig_m)

    st.write(f'Maximum positive moment: {round(max(y_positive_m) * 1e-6, 2)} kN.m')
    st.write(f'Maximum negative moment: {round(min(y_negative_m) * 1e-6, 2)} kN.m')

    #SHEAR


    shear_array = Model.Members[f'{beam_name}'].shear_array('Fy', 1000, 'LC4a')
    x_s = shear_array[0]
    y_s = shear_array[1]

    y_positive_s = np.where(y_s > 0, y_s, 0)  # Positive values of y_s
    y_negative_s = np.where(y_s < 0, y_s, 0)  # Negative values of y_s

    fig_s.add_trace(
                go.Scatter(
                    x=x_s, 
                    y=[0]*len(x_s),
                    line={"color": "green"},
                    name="Beam length"
                    )
                )
                        

    # Add trace for positive moment (blue fill)
    fig_s.add_trace(
        go.Scatter(
            x=x_s, 
            y=y_positive_s,
            fill='tozeroy',  # Fill area to the x-axis
            fillcolor='rgba(0, 0, 255, 0.3)',  # Blue fill with transparency
            line=dict(color='blue'),  # Line color for positive moments
            name="Positive Shear"
        )
    )

    # Add trace for negative moment (red fill)
    fig_s.add_trace(
        go.Scatter(
            x=x_s, 
            y=y_negative_s,
            fill='tozeroy',  # Fill area to the x-axis
            fillcolor='rgba(255, 0, 0, 0.3)',  # Red fill with transparency
            line=dict(color='red'),  # Line color for negative moments
            name="Negative Shear"
        )
    )

    fig_s.update_layout(
        plot_bgcolor = 'white',  #Background color
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            tickmode='auto',  # Automatically add more tick values
            nticks=20,        # Increase number of ticks on x-axis
        ),
        yaxis=dict(
            showgrid=True,  # Show grid lines on y-axis
            gridcolor='lightgray',  # Grid line color
            gridwidth=1  # Grid line width
        )
    )


    fig_s.layout.title.text = "Shear Diagram"
    fig_s.layout.xaxis.title = "Beam Length, mm"
    fig_s.layout.yaxis.title = "Resulting Shear, N"

    st.plotly_chart(fig_s)

    st.write(f'Maximum positive shear: {round(max(y_positive_s) * 1e-3, 2)} kN')
    st.write(f'Maximum negative shear: {round(min(y_negative_s) * 1e-3, 2)} kN')

    #DEFLECTION

    deflection_array = Model.Members[f'{beam_name}'].deflection_array('dy', 1000, 'LC4a')
    x_d = deflection_array[0]
    y_d = deflection_array[1]

    y_positive_d = np.where(y_d > 0, y_d, 0)  # Positive values of y_s
    y_negative_d = np.where(y_d < 0, y_d, 0)  # Negative values of y_s

    fig_d.add_trace(
                go.Scatter(
                    x=x_d, 
                    y=[0]*len(x_d),
                    line={"color": "green"},
                    name="Beam length"
                    )
                )
                        

    # Add trace for positive moment (blue fill)
    fig_d.add_trace(
        go.Scatter(
            x=x_d, 
            y=y_positive_d,
            fill='tozeroy',  # Fill area to the x-axis
            fillcolor='rgba(0, 0, 255, 0.3)',  # Blue fill with transparency
            line=dict(color='blue'),  # Line color for positive moments
            name="Positive deflection"
        )
    )

    # Add trace for negative moment (red fill)
    fig_d.add_trace(
        go.Scatter(
            x=x_d, 
            y=y_negative_d,
            fill='tozeroy',  # Fill area to the x-axis
            fillcolor='rgba(255, 0, 0, 0.3)',  # Red fill with transparency
            line=dict(color='red'),  # Line color for negative moments
            name="Negative deflection"
        )
    )

    fig_d.update_layout(
        plot_bgcolor = 'white',  #Background color
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            tickmode='auto',  # Automatically add more tick values
            nticks=20,        # Increase number of ticks on x-axis
        ),
        yaxis=dict(
            showgrid=True,  # Show grid lines on y-axis
            gridcolor='lightgray',  # Grid line color
            gridwidth=1  # Grid line width
        )
    )


    fig_d.layout.title.text = "Deflection Diagram"
    fig_d.layout.xaxis.title = "Beam Length, mm"
    fig_d.layout.yaxis.title = "Resulting deflection, mm"

    st.plotly_chart(fig_d)

    st.write(f'Maximum positive deflection: {round(max(y_positive_d), 2)} mm')
    st.write(f'Maximum negative deflection: {round(min(y_negative_d), 2)} mm')

    C = st.expander('Structural checks')

    with C:
        mr_latex, mr_value = app_module.calc_Mr2(Sx, Fy)
        st.latex(mr_latex)
        
else:
    st.warning(f'There is no imported file yet.\n'
               f'Complete the inputs on the left sidebar, download the generated .txt file and then upload it in the Analysis section.')
    
    
    
    
