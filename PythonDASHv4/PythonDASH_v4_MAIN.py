from click import style
import dash
import paramiko
import os
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
#import psycopg2 as psycopg2
from dash import dash_table
import base64
from dash import Dash, dcc, html, Input, Output, State
from dash.dependencies import Input, Output, State
import pandas as pd
import cx_Oracle as cxo
from time import sleep


# conn = cxo.connect("GIS_IN", "GIS_IN", "172.29.10.10:1521/GISIN")
# conn1 = conn.cursor()
# print('Established Database Connection')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title, image_filename = 'Main_Page', 'resources\images\logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

colors = {'background': '#ffffff', 'bodyColor': '#F2DFCE', 'text': '#0066b3'}
input_types = ['DD-MON-YY']

def get_page_heading_title():
    return html.H1(children='Time Series Analysis Dashboard', style={'textAlign': 'center', 'color': colors['text']})


def get_CCODE():
    CCODE = pd.read_sql("select * FROM in_company_param order by COMPANY_CODE", con=conn)['COMPANY_CODE'].unique().tolist()
    return CCODE

def get_kpi():
    KPI_ID = pd.read_sql("select * FROM SC_CD_KPI order by 1", con=conn)['CK_WKN'].unique().tolist()
    return KPI_ID

def comp_param_data(CCODE):
    df = pd.read_sql("select * from IN_COMPANY_PARAM where company_code= '{}' ".format(CCODE), con=conn)
    df['LAST_SALE_DATE'] = df['LAST_SALE_DATE'].apply(lambda x : pd.to_datetime(x).strftime("%d-%b-%y"))
    return df


def py_fc_method(CCODE):
    df = pd.read_sql("select * from py_fc_method where company_code= '{}' ".format(CCODE), con=conn)
    return df

def py_runtime_stats(CCODE):
    df = pd.read_sql("select SR_DESC, ITERATION_NO, TOTAL_PARTS, COMPLETED_PARTS, PENDING_PARTS, COMPLETE_PCNT, TIME_TAKEN from py_runtime_stat where company_code= '{}' order by SR_NO".format(CCODE), con=conn)
    return df


def py_scheduler(CCODE):
    if not CCODE:
        df = pd.read_sql("select * from PY_Scheduler order by Entry_Date desc", con=conn)
        df = df[['COMPANY_CODE','SCH_DATE','SCH_TIME','START_TIME','END_TIME','PROCESS_FLAG']]
        df['SCH_DATE'] = df['SCH_DATE'].apply(lambda x: str(x)[:10])

        return df
    else:
        df = pd.read_sql("select * from PY_Scheduler where company_code = '{}' and PROCESS_FLAG <> 'Y'".format(CCODE), con=conn)
        df = df[['COMPANY_CODE','SCH_DATE','SCH_TIME','START_TIME','END_TIME','PROCESS_FLAG']]
        df['SCH_DATE'] = df['SCH_DATE'].apply(lambda x: str(x)[:10])
        return df


def get_Subsidary():
    CCODE = pd.read_sql("select * FROM in_company_param order by COMPANY_CODE", con=conn)['COMPANY_CODE'].unique().tolist()
    return CCODE

def get_KPI_FLAG(Subsidiary):
    CCODE = pd.read_sql("select CK_WKN FROM SC_CD_KPI where company_code = '{}' ".format(Subsidiary), con=conn)['CK_WKN'].unique().tolist()
    return CCODE

def get_SC_CD_KPI_data(CCODE):
    df = pd.read_sql("Select * from SC_CD_KPI where CK_WKN  = '{}' ".format(CCODE), con=conn)
    return df

def get_param_id():
    param_id = pd.read_sql("select distinct(PARAM_ID) from SC_ALERT_PARAM ", con=conn)['PARAM_ID'].values.tolist()
    return param_id


app.layout =  html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

#######################LOGIN PAGE LAYOUT#####################################

login_page = html.Div(style={'backgroundColor': colors['background']}, children= [
                    html.H1(children='LOGIN',style={'margin-top':'20px','margin-left':'20px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                    #html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),style={'height': '30%', 'width': '25%'})], style={'margin-top':'20px','margin-left':'790px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                    html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right', 'margin-left': '810px'}),
                    html.Div(dcc.Input(id="ssh_hostname", type="text", placeholder="Enter SSH Hostname",className="inputbox1", style={'margin-left':'34.2%', 'width':'450px', 'height':'45px', 'padding':'10px', 'margin-top':'60px', 'font-size':'16px', 'border-width':'3px', 'border-color':'#a0a3a2'})),
                    html.Div(dcc.Input(id="ssh_username", type="text", placeholder="Enter SSH Username",className="inputbox2", style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(dcc.Input(id="ssh_password", type="password", placeholder="Enter SSH Password",className="inputbox3", style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(dcc.Input(id="db_username", type="text", placeholder="Enter DB Username",className="inputbox2", style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(dcc.Input(id="db_password", type="password", placeholder="Enter DB Password",className="inputbox3", style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(dcc.Input(id="db_hostname", type="text", placeholder="Enter DB Hostname",className="inputbox1",style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(dcc.Input(id="db_sid", type="text", placeholder="Enter DB SID",className="inputbox3", style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(dcc.Input(id="db_port_no", type="text", placeholder="Enter DB Port",className="inputbox3", style={'margin-left':'34.2%','width':'450px','height':'45px','padding':'10px','margin-top':'10px', 'font-size':'16px','border-width':'3px','border-color':'#a0a3a2'}),),
                    html.Div(html.Button('LOGIN', id='LOGIN', n_clicks=0, style={'background-color': '#D3D3D3','border-width':'0px','font-size':'20px'}),style={'margin-left':'47.4%','padding-top':'30px'}),
                    ])

                        
# **************************LOGIN PAGE CALLBACKS****************************************************
@app.callback(
    Output('url', 'pathname'),
     #Output(component_id='table', component_property='data'),
    [State(component_id='ssh_hostname', component_property='value'),
     State(component_id='db_hostname', component_property='value'),
     State(component_id='ssh_username', component_property='value'),
     State(component_id='db_username', component_property='value'),
     State(component_id='ssh_password', component_property='value'),
     State(component_id='db_sid', component_property='value'),
     State(component_id='db_port_no', component_property='value'),
     State(component_id='db_password', component_property='value')],
     [Input('LOGIN', 'n_clicks')])

def successful(ssh_hostname, db_hostname, ssh_username, db_username, ssh_password, db_sid, db_port_no, db_password, n_click):
    if n_click == 0:
        return '/login_page'
    else:
        try:
            global client, conn, curr
            # initialize the SSH client
            client = paramiko.SSHClient()
            # add to known hosts
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=ssh_hostname, username=ssh_username, password=ssh_password)
            conn = cxo.connect(db_username, db_password, '{}:{}/{}'.format(db_hostname, db_port_no, db_sid))
            curr = conn.cursor()
            print('Established Database Connection')
            return '/index_p'

        except: 
            return '/login_f'


# *********************************************APP LAYOUT FOR LOGIN-FAILED***************

login_failed = html.Div(style={'backgroundColor': colors['background']}, children= [dcc.Location(id='url_login_df', refresh=True), 
                        html.H1(children='LOGIN_FAILED',style={'margin-top':'20px','margin-left':'10px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                        dcc.Link([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right','margin-top':'20px', 'margin-left': '670px'},href = '/' ),
                        html.Div("Cannot connect to the SSH Server , Please Go Back to Login Page", id='Login_output',style={'color':'#183d22','font-family': 'serif', 'font-weight': 'bold', "text-decoration": "none",'font-size':'20px','padding-left':'500px','padding-top':'40px'}),
                        html.Br(),
                        html.Div(html.Button(id='back-button', children='Go back to Login Page', n_clicks=0, style={'border-width':'0px','font-size':'20px'}), style={'margin-left':'47%','padding-top':'30px'})
                        ])


@app.callback(
    Output('url_login_df', 'pathname'),
    [Input('back-button', 'n_clicks')])

def login_f(n_click):
        if n_click > 0:
            return '/'     


    

# **************************INDEX_PAGE LAYOUT********************************************************

index_page = html.Div(style={'backgroundColor': colors['background']}, children= [
                      html.H1(children='SCM Forecasting', style={'margin-top':'20px','margin-left':'20px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                      #html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),style={'height': '30%', 'width': '25%'})], style={'margin-top':'20px','margin-left':'790px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                      html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right', 'margin-left': '45.6%','margin-top':'20px'}),
                      html.Div([dcc.Link( html.Button('Forecasting',style={'height': '45px','width':'350px','background-color': '#D3D3D3','border-width':'0px','margin-left':'35%','font-size':'20px','margin-top':'90px'}), href='/page-1'),
                      html.Br(),
                      dcc.Link(html.Button('Runtime Statistics',style={'height': '45px','width':'350px','background-color': '#D3D3D3','border-width':'0px','margin-left':'35%','font-size':'20px','margin-top':'10px'}), href='/page-2'),
                      html.Br(),                      
                      dcc.Link(html.Button('Inventory',style={'height': '45px', 'width':'350px','background-color': '#D3D3D3','border-width':'0px','margin-left':'35%','font-size':'20px','margin-top':'10px'}), href='/page-3'),
                      html.Br(),
                      dcc.Link(html.Button('New Request',style={'height': '45px', 'width':'350px','background-color': '#D3D3D3','border-width':'0px','margin-left':'35%','font-size':'20px','margin-top':'10px'}), href='/page-4'),
                      html.Br(),
                      dcc.Link(html.Button('SC_REP_INIT_PARAM',style={'height': '45px', 'width':'350px','background-color': '#D3D3D3','border-width':'0px','margin-left':'35%','font-size':'20px','margin-top':'10px'}), href='/page-5'),
                      html.Br(),
                      dcc.Link(html.Button('Change User',style={'height': '45px', 'width':'350px','background-color': '#D3D3D3','border-width':'0px','margin-left':'35%','font-size':'20px','margin-top':'10px'}), href='/'),
                      html.Br(),
                      ])
                      ])
    



# ************************************FOORECASTING DASHBOARD CALLBACKS**************************************************************
# ---------------------------------------------------------------
@app.callback(
    Output(component_id='display_comp_param', component_property='style'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_display(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return {'display': 'none'}
    else:
        return  {'display': 'block'}


@app.callback(
    Output(component_id='table', component_property='data'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(my_dropdown_CCODE):
    data = comp_param_data(my_dropdown_CCODE).to_dict('records')
    return data 

# ----------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    [Output('BASE_DATA_popover', 'children')],
    # Output(component_id='table', component_property='data'),
    [State(component_id='my_dropdown_CCODE', component_property='value'),
     Input('BASE_DATA', 'n_clicks')],

)
def update_output(my_dropdown_CCODE, n_clicks):
    try:
        if n_clicks == 0:
            return ['']
        if ((n_clicks > 0) and ( not my_dropdown_CCODE )) :
            return ['Please select company_code to run'] 
        else:
            last_sale_date = pd.read_sql("Select LAST_SALE_DATE from IN_COMPANY_PARAM where company_code= '{}'".format(my_dropdown_CCODE), con = conn)
            last_sale_dt = last_sale_date['LAST_SALE_DATE'].apply(lambda x : pd.to_datetime(x).strftime("%d-%b-%y"))
            curr.callproc('RUN_BASE_DATA', [my_dropdown_CCODE,last_sale_dt.values[0]])
            # data = comp_param_data(my_dropdown_CCODE).to_dict('records')
            return ['EXECUTED']
    except Exception as exp:
        return ['EXCEPTION OCCURRED : database_error : "{}"'.format(exp)]

# ---------------------------------------------------------------------------------------------------------
@app.callback(
    Output(component_id='display_fc_method', component_property='style'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_display_method(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return {'display': 'none'}
    else:
        return  {'display': 'block'}


# ---------------------------------------------------------------------------------------------------------
@app.callback(
    Output(component_id='table_2', component_property='data'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(my_dropdown_CCODE):
    data = py_fc_method(my_dropdown_CCODE).to_dict('records')
    return data


@app.callback(
    Output(component_id='table_3', component_property='data'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(my_dropdown_CCODE):
    if not my_dropdown_CCODE :
        my_dropdown_CCODE = ''
        data = py_scheduler(my_dropdown_CCODE).to_dict('records')
        return data
    else:
        data = py_scheduler(my_dropdown_CCODE).to_dict('records')
        return data

@app.callback(
    Output(component_id='table_3_display', component_property='style'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table_3_display(my_dropdown_CCODE):
    data = py_scheduler(my_dropdown_CCODE).to_dict('records')
    if len(data) < 1:
        return {'display':'none'}

@app.callback(
    Output(component_id='Empty_table_3_display', component_property='style'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_Empty_table_3_display(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return {'display':'none'}
    else :
        data = py_scheduler(my_dropdown_CCODE).to_dict('records')
        if len(data) < 1 :
            return {'display':'block'}
        else : 
            return {'display':'none'}
        

@app.callback(
    Output(component_id='Update_scheduler_display', component_property='style'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def uUpdate_scheduler_display(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return {'display':'none'}
    else :
        data = py_scheduler(my_dropdown_CCODE).to_dict('records')
        if len(data) < 1 :
            return {'display':'none'}
        else : 
            return {'display':'block'}
               
# --------------------------------------------------------------------------------------------------------------
@app.callback(
    [Output('SUBMIT_popover', 'children')],
    # Output(component_id='table', component_property='data'),
    [State(component_id='my_dropdown_CCODE', component_property='value')],
    [State(component_id='input_date', component_property='value'),
     Input('submit-val', 'n_clicks')]
)
def update_output(my_dropdown_CCODE, input_date, n_clicks):
    try:
        if (n_clicks == 0):
            return [' ']

        elif(n_clicks > 0) and not input_date:
            return ['Please enter date then press submit']
        elif(n_clicks > 0) and not my_dropdown_CCODE:
            return ['Please select company code then press submit']
        else:
            curr.callproc('UPDATE_PY_FC_DATE', [my_dropdown_CCODE, input_date])
            # data = comp_param_data(my_dropdown_CCODE).to_dict('records')
            return ['Executed']
    except Exception as exp:
        return ['EXCEPTION OCCURRED : database_error : "{}"'.format(exp)]

#------------------------------------------------------------------------------------------------------
@app.callback(
    Output(component_id='Update_Button_display', component_property='style'),
    Input(component_id='my_dropdown_CCODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_display_method(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return {'display': 'none'}
    else:
        return  {'display': 'block'}
# -------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('Update_Method_popover', 'children'),
    [State('table_2', 'data'),
     State('table_2', 'columns'),
     Input('update_method', 'n_clicks')])

def display_output(rows, columns,n_clicks):
    try :
        if n_clicks == 0 :
            return [' ']
        elif n_clicks > 0 and not rows:
            return ['Please select company code to update method']
        elif n_clicks > 0 and not columns:
            return ['Please select company code to update method'] 
        else :
            df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
            if df.shape[0] == 0:
                return 'Please update data and methods'
            q = []
            for i in df.iterrows():
                l = []
                index = i[1].index.tolist()
                for k in index:
                    l.append(i[1][k])
                q.append(l)
            for i in q:
                curr.callproc('UPDATE_PY_METHOD_FLAG', i)
            return 'EXECUTED '
    except Exception as exp:
        return 'Exception occured : "{}"'.format(exp)

# -----------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('scheduler_popover', 'children'),
    [State(component_id='my_dropdown_CCODE', component_property='value'),
     State(component_id='scheduled_date', component_property='value'),
     State(component_id='scheduled_time', component_property='value')],
     Input('SCHEDULER', 'n_clicks')
)
def update_output(my_dropdown_CCODE,scheduled_date,scheduled_time,n_clicks):
    try:
        if n_clicks == 0:
            return [' ']
        
        elif (n_clicks) > 0 and not my_dropdown_CCODE  :
            return ['Select Company Code first to Schedule the Job']
        
        elif (n_clicks) > 0 and not scheduled_date:
            return ['Enter Schedule Date first to Schedule the Job']
        
        elif (n_clicks) > 0 and not scheduled_time :
            return ['Enter Schedule Time first to Schedule the Job']
        
        elif (n_clicks) > 0 and len(scheduled_time.split('.'))>1:
            return ['Enter the Schedule Time in correct format (HH:MM)']
        else:
            curr.callproc('CREATE_SCHEDULER_ENTRY', [my_dropdown_CCODE,'N',scheduled_date,scheduled_time])
            stdin1, stdout1, stderr1 = client.exec_command('ps -ef|grep sysapps/python_scheduler.py')
            stdin2, stdout2, stderr2 = client.exec_command('ps -ef|grep scripts/python_scheduler.py')
            state1 = stdout1.read().decode()
            state2 = stdout2.read().decode()
            state1 = state1.split('\n')
            state2 = state2.split('\n')
            counter = 0
            for s1, s2 in zip(state1, state2):
                if 'python sysapps/python_scheduler.py' in s1 or 'python scripts/python_scheduler.py' in s2:
                    counter = counter + 1
                else:
                    pass
            if counter > 0:
                return ['Forecasting Framework Execution Scheduled for Company Code : ', my_dropdown_CCODE, '\nScheduler is Running']
            else:
                return['Forecasting Framework Execution Scheduled for Company Code : ', my_dropdown_CCODE, "\nScheduler is NOT Running, Please execute 'sysapps/python_scheduler.py' manually."]
                        #return ['Framework Run Scheduled : For COMPANY_CODE "{}"  and date "{}" and time "{}" '.format(my_dropdown_CCODE,scheduled_date,scheduled_time)]
                        

    except Exception as exp:
        return ['EXCEPTION OCCURRED : database_error : "{}"'.format(exp)]

@app.callback(
    Output('PY_SCHEDULER_Header', 'children'),
    [Input(component_id = 'my_dropdown_CCODE', component_property = 'value')]
)
def update_PY_SCHEDULER_HEADER(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return 'SCHEDULED JOBS'
    else:
        return ["SCHEDULED JOBS FOR {}".format(my_dropdown_CCODE)]

@app.callback(
    Output('PY_SCHEDULER_HEADER_DISPLAY', 'style'),
    [Input(component_id='my_dropdown_CCODE', component_property='value')]
)
def update_PY_SCHEDULER_HEADER_DISPLAY(my_dropdown_CCODE):
    if not my_dropdown_CCODE:
        return {'display':'block'}
    else:
        data = py_scheduler(my_dropdown_CCODE).to_dict('records')
        if len(data) < 1:
            return {'display':'none'}
        

@app.callback(
    Output('Update_Scheduler_popover', 'children'),
    [State('table_3', 'data'),
     State('table_3', 'columns')],
    State(component_id='my_dropdown_CCODE', component_property='value'),
    Input('update_scheduler', 'n_clicks')
)
def Update_scheduler_popover(rows, columns,my_dropdown_CCODE,n_clicks):
        try :
            if n_clicks == 0 :
                return [' ']
            elif n_clicks > 0 and not rows:
                return ['Please select company code to update flag']
            elif n_clicks > 0 and not columns:
                return ['Please select company code to update flag'] 
            elif n_clicks > 0 and not my_dropdown_CCODE:
                return ['Please select company code to update flag']
            else :
                df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
                if df.shape[0] == 0:
                    return 'Please update data and methods'
                q = []
                for i in df.iterrows():
                    l = []
                    index = i[1].index.tolist()
                    for k in index:
                        l.append(i[1][k])
                    q.append(l)
                for i in q:
                    curr.callproc('CREATE_SCHEDULER_ENTRY', [i[0], i[5], None, None])
                return 'EXECUTED'
        except Exception as exp:
            return 'Exception occured : "{}"'.format(exp)




# ***************************************************RUNTIME STATS PAGE callbacks***************************************************

# ---------------------------------------------------------------
@app.callback(
    Output(component_id= 'display_stats', component_property='style'),
    [Input(component_id='dropdown_CCODE', component_property='value'),
     Input('interval-component', 'n_intervals')]
     #State(component_id='table', component_property= 'data')
)
def update_table(dropdown_CCODE, n):
    if not dropdown_CCODE :
        return {'display':'none'}
    else :
        return {'display':'block'}
    return data


@app.callback(
    Output(component_id='stats_table', component_property='data'),
    [Input(component_id='dropdown_CCODE', component_property='value'),
     Input('interval-component', 'n_intervals')]
     #State(component_id='table', component_property= 'data')
)
def update_table(dropdown_CCODE, n):
    curr.callproc('REFRESH_RUNTIME_STAT', [dropdown_CCODE])
    data = py_runtime_stats(dropdown_CCODE).to_dict('records')
    return data

#*****************************************************Inventory Page Callbacks***********************************

@app.callback(
    Output(component_id='KPI_FLAG_CODE', component_property='options'),
    Input(component_id='Subsidiary', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def batch_options(Subsidiary):
    return [{"label": i, "value": i} for i in get_KPI_FLAG(Subsidiary)]  



@app.callback(
    Output(component_id='Inventory_table', component_property='data'),
    Input(component_id='KPI_FLAG_CODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(KPI_FLAG_CODE):
    data = get_SC_CD_KPI_data(KPI_FLAG_CODE).to_dict('records')
    return data

@app.callback(
    Output(component_id='Statistics_table', component_property='data'),
    [State(component_id='Subsidiary', component_property='value'),
    State(component_id='period_flag', component_property='value'),
    State(component_id='last_sale_date', component_property='value')],
    Input('Show_Statistics_submit', 'n_clicks')
)
def get_statistics_table(Subsidiary,period_flag,last_sale_date,n_clicks):
    try:
        
        if(n_clicks > 0) and not last_sale_date:
            df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
            doc_id = df['LAST_SALE_DATE'][0].strftime("%Y%m%d")
            stats_data = pd.read_sql("select * from VIEW_SC_ALERT_DATA_SUMMARY where company_code = '{}' and period_flag = '{}' and doc_id = '{}'".format(Subsidiary,period_flag,doc_id), con=conn).to_dict('records')
            return stats_data
        else:
            # df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
            doc_id = pd.to_datetime(last_sale_date).strftime("%Y%m%d")
            stats_data = pd.read_sql("select FLAG_DESC ,PART_COUNT from VIEW_SC_ALERT_DATA_SUMMARY where company_code = '{}' and period_flag = '{}' and doc_id = '{}'".format(Subsidiary,period_flag,doc_id), con=conn).to_dict('records')
            return stats_data
    except Exception as exp:
        'Exception occured : "{}"'.format(exp)


@app.callback(
    Output('display_SC_CD_KPI', 'style'),
    [Input(component_id='KPI_FLAG_CODE', component_property='value')]
)
def update_display_SC_CD_KPI(KPI_FLAG_CODE):
    if not KPI_FLAG_CODE:
        return {'display':'none'}
    else:
        # data = get_SC_CD_KPI_data(KPI_FLAG_CODE).to_dict('records')
        # if len(data) < 1:
        #     return {'display':'none'}
        return {'display':'block'}


@app.callback(
    Output('display_Statisics', 'style'),
    [Input(component_id='Subsidiary', component_property='value'),
    State(component_id='period_flag', component_property='value'),
    State(component_id='last_sale_date', component_property='value')],
    Input('Show_Statistics_submit', 'n_clicks')
)
def update_display_Statisics(Subsidiary,period_flag,last_sale_date,n_clicks):
    try:
        if n_clicks == 0 :
            return {'display':'none'}
        elif (n_clicks > 0) and not Subsidiary:
            return {'display':'none'}

        elif (n_clicks > 0) and not period_flag:
            return {'display':'none'}

        elif(n_clicks > 0) and not last_sale_date:
                df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
                doc_id = df['LAST_SALE_DATE'][0].strftime("%Y%m%d")
                stats_data = pd.read_sql("select * from VIEW_SC_ALERT_DATA_SUMMARY where company_code = '{}' and period_flag = '{}' and doc_id = '{}'".format(Subsidiary,period_flag,doc_id), con=conn)
                if len(stats_data) > 0 :
                    return  {'display': 'block'}
        else:
            # df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
            doc_id = pd.to_datetime(last_sale_date).strftime("%Y%m%d")
            stats_data = pd.read_sql("select FLAG_DESC ,PART_COUNT from VIEW_SC_ALERT_DATA_SUMMARY where company_code = '{}' and period_flag = '{}' and doc_id = '{}'".format(Subsidiary,period_flag,doc_id), con=conn)
            if len(stats_data) > 0 :
                    return  {'display': 'block'}
    except Exception as exp:
        'Exception occured : "{}"'.format(exp)



@app.callback(
    Output(component_id='Update_table_display', component_property='style'),
    Input(component_id='KPI_FLAG_CODE', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def Update_table_display(KPI_FLAG_CODE):
    if not KPI_FLAG_CODE:
        return {'display': 'none'}
    else:
        data = get_SC_CD_KPI_data(KPI_FLAG_CODE).to_dict('records')
        if len(data) > 0 :
            return  {'display': 'block'}


@app.callback(
    Output('Update_table_popover', 'children'),
    [State('Inventory_table', 'data'),
     State('Inventory_table', 'columns'),
     Input('update_table', 'n_clicks')])

def display_output(rows, columns,n_clicks):
    try :
        if n_clicks == 0 :
            return [' ']
        elif n_clicks > 0 and not rows:
            return ['Please select company code to update method']
        elif n_clicks > 0 and not columns:
            return ['Please select company code to update method'] 
        else :
            df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
            if df.shape[0] == 0:
                return 'Please update data and methods'
            q = []
            for i in df.iterrows():
                l = []
                index = i[1].index.tolist()
                for k in index:
                    l.append(i[1][k])
                q.append(l)
            for i in q:
                curr.callproc('SC_UPDATE_KPI_VALUE', i)
            return 'EXECUTED '
    except Exception as exp:
        return 'Exception occured : "{}"'.format(exp)

@app.callback(
    Output('Get_KPI_Alert_popover', 'children'),
    [State(component_id='Subsidiary', component_property='value'),
    State(component_id='KPI_FLAG_CODE', component_property='value'),
    State(component_id='period_flag', component_property='value'),
    State(component_id='last_sale_date', component_property='value')],
    Input('Generate_KPI', 'n_clicks')
)
def update_kpi_alert(Subsidiary,KPI_FLAG_CODE,period_flag,last_sale_date,n_clicks):
    try :
        if n_clicks == 0 :
            return [' ']
        elif (n_clicks > 0) and not Subsidiary:
            return ['Please select Subsidary Code to generate alert']
        elif (n_clicks > 0) and not KPI_FLAG_CODE:
            return ['Please select KPI_FLAG_CODE to generate alert'] 
        elif (n_clicks > 0) and not period_flag:
            return ['Please select period_flag to generate alert'] 
        elif(n_clicks > 0) and not last_sale_date:
            df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
            doc_id = df['LAST_SALE_DATE'][0].strftime("%Y%m%d")
            period = df['LAST_SALE_DATE'][0].strftime("%Y%m")
            out = curr.callproc('SC_CREATE_KPI_ALERT', [Subsidiary,doc_id,period,KPI_FLAG_CODE,period_flag])
            return 'EXECUTED' 
        else:
            # df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
            doc_id = pd.to_datetime(last_sale_date).strftime("%Y%m%d")
            period = pd.to_datetime(last_sale_date).strftime("%Y%m")
            out = curr.callproc('SC_CREATE_KPI_ALERT', [Subsidiary,doc_id,period,KPI_FLAG_CODE,period_flag])
            return 'EXECUTED' 
    except Exception as exp:
        return ['Exception Occured : "{}"'.format(exp)]


@app.callback(
    Output('Show_Statistics_popover', 'children'),
    [State(component_id='Subsidiary', component_property='value'),
    State(component_id='period_flag', component_property='value'),
    State(component_id='last_sale_date', component_property='value')],
    Input('Show_Statistics_submit', 'n_clicks')
)
def update_Statisics_popover(Subsidiary,period_flag,last_sale_date,n_clicks):
    try:
        if n_clicks == 0 :
            return [' ']
        elif (n_clicks > 0) and not Subsidiary:
            return ['Please select Subsidary Code to generate Statistics']
        elif (n_clicks > 0) and not period_flag:
            return ['Please select period_flag to generate Statistics'] 
        elif(n_clicks > 0) and not last_sale_date:
                df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
                doc_id = df['LAST_SALE_DATE'][0].strftime("%Y%m%d")
                stats_data = pd.read_sql("select * from VIEW_SC_ALERT_DATA_SUMMARY where company_code = '{}' and period_flag = '{}' and doc_id = '{}'".format(Subsidiary,period_flag,doc_id), con=conn)
                if len(stats_data) > 0 :
                    return  'Statistics Generated'
        else:
            # df = pd.read_sql("select LAST_SALE_DATE FROM in_company_param where COMPANY_CODE = '{}'".format(Subsidiary), con=conn)
            doc_id = pd.to_datetime(last_sale_date).strftime("%Y%m%d")
            stats_data = pd.read_sql("select FLAG_DESC ,PART_COUNT from VIEW_SC_ALERT_DATA_SUMMARY where company_code = '{}' and period_flag = '{}' and doc_id = '{}'".format(Subsidiary,period_flag,doc_id), con=conn)
            if len(stats_data) > 0 :
                    return  'Statistics Generated'
    except Exception as exp:
        return "Exception occured : '{}'".format(exp)



@app.callback(
    Output('Report_generation_popover', 'children'),
    [State(component_id='Subsidiary', component_property='value')],
    # State(component_id='KPI_FLAG_CODE', component_property='value'),
    # State(component_id='period_flag', component_property='value'),
    # State(component_id='last_sale_date', component_property='value')],
    Input('Report_generation_submit', 'n_clicks')

)

def generate_report(Subsidiary,n_clicks):
    try:
        if n_clicks == 0:
            return ' '
        elif (n_clicks > 0) and not Subsidiary :
            return_value = os.system('python AlertReportGeneration_v1/AlertReportGeneration_v1.py')
            if return_value == 0:
                return 'Report Generated Successfully'
            else :
                return 'Error in generating report'
        
    except Exception as exp:
        return ['Exception Occured : "{}"'.format(exp)]
    

 #************************************************NEW REQUEST CALLBACKS**********************************************

@app.callback(
    Output(component_id='sc_alert_param_table', component_property='data'),
    Input(component_id='param_id', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(param_id):
    data = pd.read_sql("Select * from SC_ALERT_PARAM where PARAM_ID  = '{}' ".format(param_id), con=conn).to_dict('records')
    return data

@app.callback(
    Output(component_id='display_sc_alert_param', component_property='style'),
    Input(component_id='param_id', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def Update_button_display(param_id):
    if not param_id:
        return {'display': 'none'}
    else:
        df = pd.read_sql("Select * from SC_ALERT_PARAM where PARAM_ID  = '{}' ".format(param_id), con=conn)
        if len(df.to_dict('records')) > 0 :
            return  {'display': 'block'}


@app.callback(
    Output(component_id='Button_display', component_property='style'),
    Input(component_id='param_id', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def Update_button_display(param_id):
    if not param_id:
        return {'display': 'none'}
    else:
        df = pd.read_sql("Select * from SC_ALERT_PARAM where PARAM_ID  = '{}' ".format(param_id), con=conn)
        if len(df.to_dict('records')) > 0 :
            return  {'display': 'block'}




@app.callback(
    Output('Update_sc_alert_param_popover', 'children'),
    [State('sc_alert_param_table', 'data'),
     State('sc_alert_param_table', 'columns'),
     Input('update_sc_alert_param', 'n_clicks')])

def display_output(rows, columns,n_clicks):
    try :
        if n_clicks == 0 :
            return [' ']
        elif n_clicks > 0 and not rows:
            return ['Please select param id to update param_id_table']
        elif n_clicks > 0 and not columns:
            return ['Please select param id to update param_id_table'] 
        else :
            df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
            if df.shape[0] == 0:
                return 'Please update data'
            q = []
            for i in df.iterrows():
                l = []
                index = i[1].index.tolist()
                for k in index:
                    l.append(i[1][k])
                q.append(l)
            for i in q:
                curr.callproc('update_sc_alert_param', i)
            return 'EXECUTED '
    except Exception as exp:
        return 'Exception occured : "{}"'.format(exp)

# *********************************************SC_REP_INIT_PARAM Callbacks**********************************************

@app.callback(
    Output(component_id='SC_REP_INIT_table', component_property='data'),
    Input(component_id='ccode_sc_rep_init', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(ccode_sc_rep_init):
    if not ccode_sc_rep_init:
        data = pd.read_sql("Select * from SC_REP_INIT_PARAM where COMPANY_CODE  = '{}' ".format(ccode_sc_rep_init), con=conn)
        data = data.to_dict('records')
        return data
    else:
        data = pd.read_sql("Select * from SC_REP_INIT_PARAM where COMPANY_CODE  = '{}' ".format(ccode_sc_rep_init), con=conn)
        data['LAST_SALE_DATE'] = data['LAST_SALE_DATE'].dt.strftime("%d-%b-%y")
        data = data.to_dict('records')
        return data

@app.callback(
    Output('COMPANY_CODE_NAME', 'children'),
    Input(component_id='ccode_sc_rep_init', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def update_table(ccode_sc_rep_init):
    if not ccode_sc_rep_init:
        return ''
    else:
        data = pd.read_sql("Select COMPANY_NAME from in_company_param where COMPANY_CODE  = '{}' ".format(ccode_sc_rep_init), con=conn)
        return data['COMPANY_NAME'][0].upper()

@app.callback(
    Output(component_id='display_sc_rep_init', component_property='style'),
    Input(component_id='ccode_sc_rep_init', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def Update_button_display(ccode_sc_rep_init):
    if not ccode_sc_rep_init:
        return {'display': 'none'}
    else:
        df = pd.read_sql("Select * from SC_REP_INIT_PARAM where COMPANY_CODE  = '{}' ".format(ccode_sc_rep_init), con=conn)
        if len(df.to_dict('records')) > 0 :
            return  {'display': 'block'}
        else :
            return {'display': 'none'}

@app.callback(
    Output(component_id='SC_REP_Button_display', component_property='style'),
    Input(component_id='ccode_sc_rep_init', component_property='value'),
    # State(component_id='table', component_property= 'data')
)
def Update_button_display(ccode_sc_rep_init):
    if not ccode_sc_rep_init:
        return {'display': 'none'}
    else:
        df = pd.read_sql("Select * from SC_REP_INIT_PARAM where COMPANY_CODE  = '{}' ".format(ccode_sc_rep_init), con=conn)
        if len(df.to_dict('records')) > 0 :
            return  {'display': 'block'}

@app.callback(
    Output('Update_SC_REP_INIT_PARAM_popover', 'children'),
    [State('SC_REP_INIT_table', 'data'),
     State('SC_REP_INIT_table', 'columns'),
     Input('update_REP_INIT_PARAM', 'n_clicks')])

def display_output(rows, columns,n_clicks):
    try :
        if n_clicks == 0 :
            return [' ']
        elif n_clicks > 0 and not rows:
            return ['Please select Company_code to update SC_REP_INIT_PARAM_table']
        elif n_clicks > 0 and not columns:
            return ['Please select Company_code to update SC_REP_INIT_PARAM_table'] 
        else :
            df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
            if df.shape[0] == 0:
                return ['NO Data Available for selected company_code']
            q = []
            for i in df.iterrows():
                l = []
                index = i[1].index.tolist()
                for k in index:
                    l.append(i[1][k])
                q.append(l)
            try : 
                for i in q:
                    curr.callproc('update_sc_rep_init_param', i)
            except Exception as exp:
                return ["Exception Occured : '{}'".format(exp)]
            return ['EXECUTED']
    except Exception as exp:
        return 'Exception occured : "{}"'.format(exp)
    

# *************************************************MAIN "APP CALLBACK " **********************************************

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    try:
        if pathname == '/':
            return login_page
        elif pathname == '/index_p':
            return index_page
        elif pathname == '/login_f':
            return login_failed
        elif pathname == '/page-2':
            return html.Div(style={'backgroundColor': colors['background']}, children=[
                   html.H1(children='RUN TIME STATS DASHBOARD', style={'margin-left': '10px', 'display': 'inline-block','textAlign': 'left', 'color': colors['text']}),
                   dcc.Link([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right','margin-top':'22px', 'margin-left': '378px'},href = '/index_p'),
                   html.Div([
                            html.Label(['Select Company_Code'], style={'margin-left': '10px', 'textAlign': 'left', 'color': colors['text']}),
                            dcc.Dropdown(id='dropdown_CCODE', options=[{'label': k, 'value': k} for k in get_CCODE()], multi=False, clearable=True, searchable=True, style={'margin-left': '05px',"width": "50%"}),
                            ]),
                    html.Div(id = 'display_stats', children=[
                            #html.Label(['RUNTIME_STATS']),
                            dash_table.DataTable(id='stats_table', 
                                                columns=[{"name": i, "id": i} for i in py_runtime_stats('95018-3')],
                                                style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                                style_data={'color': 'black', 'backgroundColor': 'white'},
                                                style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(220, 220, 220)',}],
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                editable=True, 
                                                style_table = {'margin-right':'10px','margin-left': '10px', 'width' : 'auto', 'overflowX': 'scroll','overflowY':'scroll'},
                                                ),
                            dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
                            ],style = {'display':'none'}),
                    html.Br()
                    ])

        elif pathname == '/page-1':
            return [html.Div(style={'backgroundColor': colors['background']}, children= [
                    html.H1(children='Forecasting Analysis',style={'margin-top':'20px','margin-left':'20px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                    #html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),style={'height': '30%', 'width': '25%'})], style={'margin-top':'20px','margin-left':'790px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                    dcc.Link([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right', 'margin-left': '40.6%'},href = '/index_p'),
                    html.Div([dcc.Dropdown(id='my_dropdown_CCODE', options=[{'label': k, 'value': k} for k in get_CCODE()],placeholder="Select Company Code", multi=False, clearable=True, searchable=True, style={'margin-left': '10px',"width": "300px",'margin-top':'20px'}),
                    dcc.Input(id='input_date'.format('DD-MON-YY'), type='DD-MON-YY', placeholder="Enter Last Sale Date ('DD-MON-YY')", debounce=True, minLength=0, maxLength=50, style = { 'margin-left': '240px',"width": "280px",'margin-top':'40px','height': '36px'}),
                    dcc.Input(id='scheduled_date'.format('DD-MON-YY'), type='DD-MON-YY', placeholder="Enter Scheduled Date ('DD-MON-YY')", debounce=True, minLength=0, maxLength=50, style = { 'margin-left': '220px',"width": "280px",'margin-top':'40px','height': '36px'})], style = {'display':'flex'}),
                    html.Div([html.Button("Run 'CREATE_BASE_DATA'", id='BASE_DATA', n_clicks=0, draggable = False,style= {'height': '40px','width':'300px','background-color': '#D3D3D3','border-width':'0px','margin-left':'20px','font-size':'20px','margin-top':'10px'}),
                    html.Button('Update Last Sale Date', id='submit-val', n_clicks=0, style= {'margin-left': '230px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'}),
                    dcc.Input(id='scheduled_time'.format('HH:MM'), type='HH:MM', placeholder="Enter Scheduled Time ('HH:MM')", debounce=True, minLength=0, maxLength=50, style = { 'margin-left': '220px','margin-top':'0px',"width": "280px",'height': '34px'})]),
                    html.Div([html.Button('Create Schedule', id='SCHEDULER', n_clicks=0, style= {'margin-left': '1050px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'})]),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="scheduler_popover", target="SCHEDULER", trigger="focus",),]),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="SUBMIT_popover", target="submit-val", trigger="focus", ),]),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="BASE_DATA_popover", target="BASE_DATA", trigger="focus",),]),
                    html.Div(id = 'display_PY_SCHEDULER', children=[
                    html.Br(),
                    html.B(id = 'PY_SCHEDULER_HEADER_DISPLAY', children = [html.Label('PY SCHEDULER', id = 'PY_SCHEDULER_Header', style={'margin-left': '530px','font-size':'22px', 'color': '#000000'})],style = {'display':'block'}),
                    html.Div(id = 'table_3_display', children = [
                            dash_table.DataTable(id='table_3',
                                                columns=[
                                                    {'id': 'COMPANY_CODE', 'name': 'COMPANY_CODE',"selectable": True},
                                                    {'id': 'SCH_DATE', 'name': 'SCH_DATE',"selectable": True},
                                                    {'id': 'SCH_TIME', 'name': 'SCH_TIME',"selectable": True},
                                                    {'id': 'START_TIME', 'name': 'START_TIME', "selectable": True},
                                                    {'id': 'END_TIME', 'name': 'END_TIME', "selectable": True}, 
                                                    {'id': 'PROCESS_FLAG', 'name': 'PROCESS_FLAG', 'presentation': 'dropdown',"selectable": True},
                                                ],
                                                css=[{"selector": ".Select-menu-outer", "rule": 'display : block !important'}],
                                                dropdown={'PROCESS_FLAG': {'options': [{'label': i, 'value': i} for i in ['C', 'N','Y','P']], 'clearable': True }},
                                                style_table={'margin-left': '10px','margin-right':'10px','height': '300px','width' : 'auto', 'overflowX': 'scroll', 'overflowY': 'scroll'},
                                                style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                                fill_width=True,
                                                style_data={'color': 'black', 'backgroundColor': 'white', 'whiteSpace': 'normal', 'height': 'auto'},
                                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)',}],
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                editable=True,
                            )],style = {'display':'block'})
                    ],style = {'display':'block'}),
                    html.Div(id = 'Empty_table_3_display',children = [html.B('NO JOBS SCHEDULED FOR THIS COMPANY CODE', style = {'margin-left':'510px','font':'60px'})], style = {'display':'none'}),
                    html.Br(),
                    html.Div(id = 'Update_scheduler_display', children = [html.Button('Update Scheduler', id='update_scheduler', n_clicks=0, draggable = False, style= {'margin-left': '550px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'})], style = {'display':'block'} ),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"), ], placement="bottom", id="Update_Scheduler_popover", target="update_scheduler", trigger="focus", )]),
                    html.Br(),            
                    html.Div(id = "display_comp_param", children=[
                            html.Br(),
                            html.B(html.Label(['General Details'],style = {'margin-left': '616px','font-size':'22px', 'color': '#000000'})),
                            dash_table.DataTable(id='table', 
                                                columns=[{"name": i, "id": i} for i in comp_param_data('95018-3')],
                                                #data=comp_param_data('95018-3').to_dict('records'),
                                                style_cell={'textAlign': 'center'},
                                                style_data={'color': 'black', 'backgroundColor': 'white'},
                                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)', }],
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                editable=True, 
                                                style_table = {'margin-right':'10px','margin-left': '10px', 'width' : 'auto', 'overflowX': 'scroll','overflowY':'scroll'}
                                            ),
                            ],style = {'display': 'none'}),
                    html.Div(id = 'display_fc_method', children=[
                            html.Br(),
                            html.B(html.Label(['Method Selection'],style={'margin-left': '605px','font-size':'22px', 'color': '#000000'})),
                            dash_table.DataTable(id='table_2',
                                            columns=[
                                                {'id': 'COMPANY_CODE', 'name': 'COMPANY_CODE'},
                                                {'id': 'ITERATION_NO', 'name': 'ITERATION_NO'},
                                                {'id': 'METHOD_NAME', 'name': 'METHOD_NAME'},
                                                {'id': 'BLOCKED', 'name': 'BLOCKED', 'presentation': 'dropdown'},
                                            ],
                                            #data=py_fc_method('95018-3').to_dict('records'),
                                            css=[{"selector": ".Select-menu-outer", "rule": 'display : block !important'}],
                                            dropdown={
                                                'BLOCKED': {
                                                    'options': [{'label': i, 'value': i} for i in ['Y', 'N']],
                                                    'clearable': True
                                                }
                                            },
                                            style_table={'margin-left': '10px','margin-right':'10px','height': '300px', 'width' : 'auto', 'overflowX': 'scroll'},
                                            style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                            fill_width=True,
                                            style_data={
                                                'color': 'black',
                                                'backgroundColor': 'white',
                                                'whiteSpace': 'normal',
                                                'height': 'auto'
                                            },
                                            style_data_conditional=[
                                                {
                                                    'if': {'row_index': 'odd'},
                                                    'backgroundColor': 'rgb(220, 220, 220)',
                                                }
                                            ],
                                            
                                            style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black',
                                                        'fontWeight': 'bold', 'border': '1px solid black'},

                                            editable=True,
                                            
                                            )
                            ],style = {'display':'none'}),
                    html.Div(id = 'Update_Button_display', children = [html.Button('Update Method', id='update_method', n_clicks=0, draggable = False, style= {'margin-left': '550px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'})],style = {'display':'none'}),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"), ], placement="bottom", id="Update_Method_popover", target="update_method", trigger="focus", )]), 
                    html.Br(),
                    ])]

        elif pathname == '/page-3':
            return [html.Div(style={'backgroundColor': colors['background']}, children= [
                    html.H1(children='Inventory Dashboard', style={'margin-top':'20px','margin-left':'20px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                    #html.Div([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),style={'height': '30%', 'width': '25%'})], style={'margin-top':'20px','margin-left':'790px','display': 'inline-block','textAlign': 'centre', 'color': colors['text']}),
                    dcc.Link([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right', 'margin-left': '40.6%'},href = '/index_p'),
                    html.Div([dcc.Dropdown(id='Subsidiary', options=[{'label': k, 'value': k} for k in get_Subsidary()],placeholder="Select Subsidary Code", multi=False, clearable=True, searchable=True, style={'margin-left': '10px',"width": "300px",'margin-top':'30px'})]),
                    html.Div([
                            dcc.Dropdown(id='KPI_FLAG_CODE',placeholder="Select KPI_Flag", multi=False, clearable=True, searchable=True, style={'margin-left': '10px',"width": "300px",'margin-top':'0px'}),
                            dcc.Input(id='last_sale_date'.format('DD-MON-YY'), type='DD-MON-YY', placeholder="Enter Last Sale Date ('DD-MON-YY')", debounce=True, minLength=0, maxLength=50, style = { 'margin-left': '240px',"width": "280px",'margin-top':'0px','height': '36px'}),
                            dcc.Dropdown(id='period_flag', options=[{'label': k, 'value': k} for k in ['CUR','YTD','M36','LST']],placeholder="Select period flag", multi=False, clearable=True, searchable=True, style={'margin-left': '114px',"width": "280px",'margin-top':'0px'}),
                            ],style = {'display':'flex'}),
                    html.Div([html.Button("'Get_KPI_Alert'", id='Generate_KPI', n_clicks=0, draggable = False,style= {'height': '40px','width':'300px','background-color': '#D3D3D3','border-width':'0px','margin-left':'20px','font-size':'20px','margin-top':'10px'}),
                            html.Button('Show Statistics', id='Show_Statistics_submit', n_clicks=0, style= {'margin-left': '230px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'}),
                            html.Button('Generate KPI Report', id='Report_generation_submit', n_clicks=0, style= {'margin-left': '230px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'}),
                            ]),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"), ], placement="bottom", id="Get_KPI_Alert_popover", target="Generate_KPI", trigger="focus", )]),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"), ], placement="bottom", id="Show_Statistics_popover", target="Show_Statistics_submit", trigger="focus",)]),
                    html.Div(id = 'display_SC_CD_KPI', children=[
                            html.Br(),
                            html.B(html.Label(['SC_CD_KPI'],style={'margin-left': '605px','font-size':'22px', 'color': '#000000'})),
                            dash_table.DataTable(id='Inventory_table',
                                                #  data = get_SC_CD_KPI_data('K001').to_dict('records'),
                                                #columns=[{"name": i, "id": i} for i in get_SC_CD_KPI_data('K001')],
                                                columns = [
                                                    {'id': 'CK_WKN', 'name': 'CK_WKN'},
                                                    {'id': 'CK_WKL', 'name': 'CK_WKL'},
                                                    {'id': 'CK_CATEG', 'name': 'CK_CATEG'},
                                                    {'id': 'CK_MODEL', 'name': 'CK_MODEL'},
                                                    {'id': 'CK_PART', 'name': 'CK_PART'},
                                                    {'id': 'CK_TGT', 'name': 'CK_TGT'},
                                                    {'id': 'CK_PERIOD', 'name': 'CK_PERIOD'},
                                                    {'id': 'CK_COD', 'name': 'CK_COD', 'editable' : True},
                                                    {'id': 'CK_ATR', 'name': 'CK_ATR'},
                                                    {'id': 'CK_VAL', 'name': 'CK_VAL', 'editable' : True},
                                                    {'id': 'CK_ERR', 'name': 'CK_ERR'},
                                                    {'id': 'CK_TGT_NAME', 'name': 'CK_TGT_NAME'},

                                                    ],
                                                css=[{"selector": ".Select-menu-outer", "rule": 'display : block !important'}],
                                                page_action='none',
                                                style_table={'margin-left': '20px','margin-right':'10px','height': '300px', 'width' : 'auto', 'overflowX': 'scroll'},
                                                style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                                fill_width=True,
                                                style_data={'color': 'black', 'backgroundColor': 'white', 'whiteSpace': 'normal', 'height': 'auto'},
                                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)',}], 
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                editable=False,
                                                )
                            ],style = {'display':'none'}),
                    html.Div(id = 'Update_table_display', children = [html.Button('Update SC_CD_KPI', id='update_table', n_clicks=0, draggable = False, style= {'margin-left': '550px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'})],style = {'display':'none'}),
                    html.Div([dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="Update_table_popover", target="update_table", trigger="focus", )]),
                    html.Div([dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="Report_generation_popover", target="Report_generation_submit", trigger="focus", )]),
                    html.Br(),
                    html.Div(id = 'display_Statisics', children=[
                            html.Br(),
                            html.B(html.Label(['Inventory Statistics'],style={'margin-left': '605px','font-size':'22px', 'color': '#000000'})),
                            dash_table.DataTable(id='Statistics_table',
                                                #data = get_SC_CD_KPI_data('K001').to_dict('records'),
                                                #columns=[{"name": i, "id": i} for i in get_SC_CD_KPI_data('K001')],
                                                columns = [
                                                            {'id': 'FLAG_DESC', 'name': 'FLAG_DESC'},
                                                            {'id': 'PART_COUNT', 'name': 'PART_COUNT'},
                                                        ],
                                                css=[{"selector": ".Select-menu-outer", "rule": 'display : block !important'}],
                                                page_action='none',
                                                fixed_rows={'headers': True},
                                                style_table={'margin-left': '10px','margin-right':'10px','height': 'auto', 'width' : 'auto', 'overflowX': 'scroll', 'overflowY': 'scroll'},
                                                style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                                fill_width=True,
                                                style_data={'color': 'black', 'backgroundColor': 'white', 'whiteSpace': 'normal', 'height': 'auto' },
                                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)', }],
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                editable=False,
                                            
                                                )
                            ],style = {'display':'none'}),
        ])]
        elif pathname == '/page-4':    
            return [html.Div(style={'backgroundColor': colors['background']}, children=[
                    html.H1(children='SCM_INVENTORY_PARAM', style={'margin-left': '10px', 'display': 'inline-block','textAlign': 'left', 'color': colors['text']}),
                    dcc.Link([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right','margin-top':'22px', 'margin-left': '470px'},href = '/index_p'),
                    html.Div([html.Label(['Select param_id'], style={'margin-left': '10px', 'textAlign': 'left', 'color': colors['text']}),
                            dcc.Dropdown(id='param_id', options=[{'label': k, 'value': k} for k in get_param_id()], multi=False, clearable=True, searchable=True, style={'margin-left': '05px',"width": "50%"} ),
                            ]),
                    html.Br(),
                    html.Div(id = 'display_sc_alert_param', children=[html.Br(),
                            html.B(html.Label(['SC_ALERT_PARAM'],style={'margin-left': '605px','font-size':'22px', 'color': '#000000'})),
                            dash_table.DataTable(id='sc_alert_param_table',
                                                #  data = get_SC_CD_KPI_data('K001').to_dict('records'),
                                                #columns=[{"name": i, "id": i} for i in get_SC_CD_KPI_data('K001')],
                                                columns = [
                                                    {'id': 'PARAM_ID', 'name': 'PARAM_ID'},
                                                    {'id': 'PARAM_DESC', 'name': 'PARAM_DESC'},
                                                    {'id': 'PART_CATEG', 'name': 'PART_CATEG'},
                                                    {'id': 'PART_MODEL', 'name': 'PART_MODEL'},
                                                    {'id': 'PARAM_VALUE', 'name': 'PARAM_VALUE','editable' : True},
                                                    {'id': 'PARAM_CONDITION', 'name': 'PARAM_CONDITION','editable' : True}],
                                                css=[{"selector": ".Select-menu-outer", "rule": 'display : block !important'}],
                                                page_action='none',
                                                fixed_rows={'headers': True},
                                                style_table={'margin-left': '10px','margin-right':'10px','height': 'auto', 'overflowX': 'scroll'},
                                                style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                                fill_width=True,
                                                style_data={'color': 'black','backgroundColor': 'white','whiteSpace': 'normal', 'height': 'auto'},
                                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)',}],
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                editable=False,
                                                )
                    ],style = {'display':'none'}),
                    html.Div(id = 'Button_display', children = [html.Button('Update sc_alert_param', id='update_sc_alert_param', n_clicks=0, draggable = False, style= {'margin-left': '550px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'10px'})],style = {'display':'none'}),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="Update_sc_alert_param_popover", target="update_sc_alert_param", trigger="focus", )]),]
            )]
        elif pathname == '/page-5':
            return[html.Div(style={'backgroundColor': colors['background']}, children=[
                    html.H1(children='SC_REP_INIT_PARAM', style={'margin-left': '10px', 'display': 'inline-block','textAlign': 'left', 'color': colors['text']}),
                    dcc.Link([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'height': '30%', 'width': '50%'})], style={'display': 'inline-block', 'textAlign': 'right','margin-top':'22px', 'margin-left': '560px'},href = '/index_p'),
                    html.Div([html.Label(['Select company_code'], style={'margin-left': '10px', 'textAlign': 'left', 'color': colors['text']}),
                            dcc.Dropdown(id='ccode_sc_rep_init', options=[{'label': k, 'value': k} for k in get_CCODE()], multi=False, clearable=True, searchable=True, style={'margin-left': '05px',"width": "50%"} ),
                            ]),
                    html.Br(),
                    html.B(html.Label(children='',id = 'COMPANY_CODE_NAME' ,style={'margin-left': '10px','textAlign': 'left', 'font-size':'22px', 'color': colors['text']})),
                    html.Br(),
                    html.Div(id = 'display_sc_rep_init', children=[html.Br(),
                            dash_table.DataTable(id='SC_REP_INIT_table',
                                                #  data = get_SC_CD_KPI_data('K001').to_dict('records'),
                                                #columns=[{"name": i, "id": i} for i in get_SC_CD_KPI_data('K001')],
                                                columns = [
                                                    {'id': 'COMPANY_CODE', 'name': 'COMPANY_CODE'},
                                                    {'id': 'KPI_ID', 'name': 'KPI_ID', 'editable' : True, 'presentation': 'dropdown'},
                                                    {'id': 'PERIOD_FLAG', 'name': 'PERIOD_FLAG', 'editable' : True,'presentation': 'dropdown'},
                                                    {'id': 'LAST_SALE_DATE', 'name': 'LAST_SALE_DATE', 'editable' : True},
                                                    {'id': 'DOC_ID', 'name': 'DOC_ID', 'editable' : True},
                                                    {'id': 'ANALYSIS_FLAG', 'name': 'ANALYSIS_FLAG', 'editable' : True,'presentation': 'dropdown'}],
                                                dropdown={
                                                'PERIOD_FLAG': {
                                                    'options': [{'label': i, 'value': i} for i in ['CUR', 'M36','M72']],
                                                    'clearable': True
                                                 },
                                                 'KPI_ID': {
                                                    'options': [{'label': i, 'value': i} for i in get_kpi()],
                                                    'clearable': True
                                                 },
                                                 'ANALYSIS_FLAG': {
                                                    'options': [{'label': i, 'value': i} for i in ['PCAT','SCAT','LMDL','MMDL','SMDL']],
                                                    'clearable': True
                                                 },
                                                },
                                                css=[{"selector": ".Select-menu-outer", "rule" : 'display : block !important'}],
                                                style_table={'margin-left': '10px','margin-right':'10px','height': 'auto'},
                                                style_cell={'textAlign': 'center','height': 'auto','minWidth': '180px', 'width': '180px', 'maxWidth': '180px','whiteSpace': 'normal'},
                                                fill_width=True,
                                                style_header={'backgroundColor': 'rgb(210, 210, 210)', 'color': 'black', 'fontWeight': 'bold', 'border': '1px solid black'},
                                                style_data={'color': 'black','backgroundColor': 'white','whiteSpace': 'normal', 'height': 'auto','lineHeight': '15px'},
                                                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)',}],
                                                editable=False,
                                                )
                    ],style = {'display':'none'}),
                    html.Div(id = 'SC_REP_Button_display', children = [html.Button('Update SC_REP_INIT_PARAM', id='update_REP_INIT_PARAM', n_clicks=0, draggable = False, style= {'margin-left': '550px','height': '40px','width':'280px','background-color': '#D3D3D3','border-width':'0px','font-size':'20px','margin-top':'50px'})],style = {'display':'none'}),
                    html.Div([ dbc.Popover(children=[dbc.PopoverHeader(dbc.Row([' '])), dbc.PopoverBody("Body content"),], placement="bottom", id="Update_SC_REP_INIT_PARAM_popover", target="update_REP_INIT_PARAM", trigger="focus" ,)]),])
                ]

        else:
            return login_page
    except Exception as exp:
        return ['Exception Occured : "{}"'.format(exp)]
    


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=False)