try:
    import pandas as pd
    import numpy as np
    import seaborn as sns
    from datetime import datetime as dt
    from datetime import *; from dateutil.relativedelta import *
    import cx_Oracle as cxo
    import os
    import shutil
    from pathlib import Path
    import multiprocessing as mp
    import dataframe_image as dfi
    import warnings
    warnings.filterwarnings('ignore')
    warnings.simplefilter('ignore', DeprecationWarning)
    warnings.simplefilter('ignore', FutureWarning)
    ## Importing PDF and plot related libraries
    from fpdf import FPDF
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    rcParams['axes.spines.top'] = False
    rcParams['axes.spines.right'] = False

    try:
        ## Extracting login details from 'login_details.txt'
        login_path = os.path.join(os.getcwd(), 'AlertReportGeneration_v1/resources', 'login_details', 'login_details.txt')
        with open(login_path) as login_details:
            details = login_details.readlines()
        username = details[0].strip().split('=')[1].strip()
        password = details[1].strip().split('=')[1].strip()
        host = details[2].strip().split('=')[1].strip()
        port = details[3].strip().split('=')[1].strip()
        sid = details[4].strip().split('=')[1].strip()
        login_details.close()
        ## To extract the data from Database
        connection = cxo.connect(username, password, '{}:{}/{}'.format(host, port, sid))
        ## Printing the log
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT : DB CONNECTION ESTABLISHED')
    except Exception as exp:
        ## Printing the log
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT : UNABLE TO CONNECT TO DB :', exp)
        raise ValueError
        
    def p1(company_code, part_no):
        ## c1
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C1 : PROCESSING')
        forecast = pd.read_sql("select * from py_part_forecast_final_fc where company_code = '{}' and part_no = '{}' order by 6".format(company_code, part_no), con = connection)[['FC_PERIOD', 'QTY']]
        actual = pd.read_sql("select * from in_part_base_data where company_code = '{}' and part_no = '{}' order by 3, 4".format(company_code, part_no), con = connection)[['PERIOD', 'QTY']]
        forecast['FC_PERIOD'] = forecast['FC_PERIOD'].apply(lambda x: dt.strptime(str(x), '%Y%m'))
        actual['PERIOD'] = actual['PERIOD'].apply(lambda x: dt.strptime(str(x), '%Y%m'))
        forecast.set_index('FC_PERIOD', inplace = True)
        actual.set_index('PERIOD', inplace = True)
        ## Creating Chart
        ax = plt.figure(figsize = (15, 5))
        plt.style.use('seaborn')
        plt.plot(actual, color = 'maroon', label = 'Actual Sales')
        plt.plot(forecast, color = 'blue', label = 'Forecast')
        plt.xticks(fontsize = 9)
        plt.yticks(fontsize = 9)
        plt.xlabel('PERIOD', fontsize = 13)
        plt.ylabel('QUANTITY', fontsize = 13)
        plt.grid(b = True, which = 'minor', color = 'black', linestyle = '-')
        plt.legend(frameon = True)
        ax.patch.set_edgecolor('black')
        ax.patch.set_linewidth('2.5')  
        plt.title('{}\nComparing Actual Sales and Forecasting\n'.format(part_no), fontsize = 17)
        ## Exporting the Charts
        plt.savefig('AlertReportGeneration_v1/resources/plots/{}/c1_{}'.format(company_code, part_no), dpi = 300, bbox_inches = 'tight', pad_inches = 0.1)
        plt.close()
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C1 : PROCESSED')
        
    def p2(company_code, part_no, start_period, end_period):
        ## c2
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C2 : PROCESSING')
        stocks = pd.read_sql("select to_number(substr(date_created, 1, 6)) as period, sum(actual_on_hand_qty) as stock_in_hand, sum(nvl(actual_on_hand_qty, 0)- nvl(on_hand_available_qty, 0)) as reserved_qty from view_sc_db71_stock where subsidiary_code = '{}' and part_no = '{}' and substr(date_created, 1, 6) between {} and {} group by to_number(substr(date_created, 1, 6)) order by 1".format(company_code, part_no, start_period, end_period), con = connection)
        stocks['PERIOD'] = stocks['PERIOD'].apply(lambda x: dt.strptime(str(x), '%Y%m'))
        stocks.set_index('PERIOD', inplace = True)
        sales_info = pd.read_sql("select to_number(substr(delivery_date ,1,6)) as period, sum(order_quantity) as ord_qty from view_sc_db81_order where company_code = '{}' and part_no = '{}' and substr(delivery_date,1,6) between {} and {} group by to_number(substr(delivery_date ,1,6)) order by 1".format(company_code, part_no, start_period, end_period), con = connection)
        sales_info['PERIOD'] = sales_info['PERIOD'].apply(lambda x: dt.strptime(str(x), '%Y%m'))
        sales_info.set_index('PERIOD', inplace = True)
        actual_sales = pd.read_sql("select period, sum(qty) as sale_qty from in_part_base_data where company_code = '{}' and part_no = '{}' and substr(period,1,6) between {} and {} group by period order by 1".format(company_code, part_no, start_period, end_period), con = connection)
        actual_sales['PERIOD'] = actual_sales['PERIOD'].apply(lambda x: dt.strptime(str(x), '%Y%m'))
        actual_sales.set_index('PERIOD', inplace = True)
        periods = pd.date_range(dt.strptime(str(start_period), '%Y%m'), periods = 12, freq = 'MS')
        ## Creating Chart
        ax = plt.figure(figsize = (15, 5))
        plt.style.use('seaborn')
        bar_width = 15
        ax1 = plt.bar(stocks.index, stocks['STOCK_IN_HAND'], width = bar_width, color = 'teal', label = 'On Available')
        ax2 = plt.bar(stocks.index, stocks['RESERVED_QTY'], width = bar_width, bottom = stocks['STOCK_IN_HAND'], color = 'red', label = 'Reserved')
        plt.plot(actual_sales, color = 'coral', label = 'Actual Sale')
        plt.plot(sales_info, color = 'yellow', label = 'Sales Orders')
        plt.xticks(periods, fontsize = 10, rotation = 10)
        plt.xlabel('PERIOD', fontsize = 13)
        plt.ylabel('QUANTITY', fontsize = 13)
        plt.grid(b = True, which = 'minor', color = 'black', linestyle = '-')
        ## Enabling legend
        plt.legend(frameon = True)
        ## Title for the Chart
        plt.title('{}\nComparing Actual Sales and Inventory\n'.format(part_no), fontsize = 17)
        for r1, r2 in zip(ax1, ax2):
            h1, h2 = r1.get_height(), r2.get_height()
            plt.text(r1.get_x() + r1.get_width() / 2., h1 / 2., '%d' % h1, ha = 'center', va = 'center', color = "black", fontsize = 10)
            plt.text(r2.get_x() + r2.get_width() / 2., h1 + h2 / 2., '%d' % h2, ha = 'center', va = 'center', color = "black", fontsize = 10)
        ax.patch.set_edgecolor('black')
        ax.patch.set_linewidth('2.5')  
        ## Exporting the Charts
        plt.savefig('AlertReportGeneration_v1/resources/plots/{}/c2_{}'.format(company_code, part_no), dpi = 300, bbox_inches = 'tight', pad_inches = 0.1)
        plt.close()
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C2 : PROCESSED')
    
    def p3(company_code, part_no, start_period):
        ## c4
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C4 : PROCESSING')
        c4 = pd.read_sql("select * from view_sc_db04 where part_number = '{}' ".format(part_no), con = connection)
        c4 = c4[(c4['TRANSACTION_DATE'] > start_period)]
        c4_data = pd.DataFrame(c4.groupby('COMPANY_CODE')['INVOICED_QUANTITY'].sum().sort_values(ascending = False)[:5]).reset_index()
        list_company_code = c4_data['COMPANY_CODE'].tolist()
        others = pd.DataFrame(c4[~c4['COMPANY_CODE'].isin(list_company_code)])['INVOICED_QUANTITY'].sum()
        c4_data.loc[len(c4_data.index)] = ['Others', others]
        ## Creating Chart
        ax = plt.figure(figsize = (5, 5))
        plt.style.use('seaborn')
        plt.pie(c4_data['INVOICED_QUANTITY'], labels = c4_data['COMPANY_CODE'], startangle = 45, shadow = False, autopct = '%1.2f%%')
        plt.title('Top Company Codes')
        plt.axis('equal')
        ax.patch.set_edgecolor('black')
        ax.patch.set_linewidth('2')
        ## Exporting the Charts
        plt.savefig('AlertReportGeneration_v1/resources/plots/{}/c4_{}'.format(company_code, part_no), dpi = 300, bbox_inches = 'tight', pad_inches = 0.1)
        plt.close()
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C4 : PROCESSED')
    
    def p4(company_code, part_no):
        ## c3
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C3 : PROCESSING')
        c3_data = pd.read_sql("select * from view_sale_vs_ord where company_code = '{}'".format(company_code), con = connection)
        c4_data = c3_data
        c3_data = pd.pivot_table(c3_data, index = c3_data['TRN_FLAG'], columns = ['YEAR_NO'], values = ['QTY'], aggfunc = 'sum')
        columns = c3_data.columns.droplevel()
        c3_data.columns = columns
        c3_data.rename_axis(None, axis = 1, inplace = True)
        c3_data.rename_axis(None, axis = 0, inplace = True)
        c3_data.sort_index(ascending = False, inplace = True)
        c3 = c3_data.iloc[:, -4:]
        c3 = c3.fillna(0)
        c3_avg = []
        for i, k in c3.iterrows():
            c3_avg.append(k.values.mean())
        c3['AVG'] = c3_avg
        for column in c3.columns:
            c3[column] = c3[column].astype(int) 
        c3 = c3.style.background_gradient(cmap = 'Greys', axis = None, low = 0.75, high = 1.0)
        ## c5
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C5 : PROCESSING')
        c5 = pd.read_sql("select * from view_sc_db04 where company_code = '{}' AND PART_NUMBER = '{}' ".format(company_code, part_no), con = connection)
        prev_months = (pd.to_datetime(last_sale_date) - relativedelta(months= 12))
        c5 = c5[(c5['TRANSACTION_DATE'].apply(lambda x : dt.strptime(str(x),"%Y%m%d")) > prev_months)]
        c5 = pd.DataFrame(c5.groupby('CUSTOMER_NAME')['INVOICED_QUANTITY'].sum().sort_values(ascending = False)[:5]).reset_index()
        country_code = pd.read_sql("select COUNTRY_CODE from in_company_param where company_code = '{}'".format(company_code), con = connection)['COUNTRY_CODE'][0]
        c5['Company_Code'] = company_code
        c5['Country_Code'] = country_code
        c5 = c5[['CUSTOMER_NAME', 'Company_Code', 'Country_Code', 'INVOICED_QUANTITY']]
        c5['INVOICED_QUANTITY'] = c5['INVOICED_QUANTITY'].astype(int)
        c5.rename({'CUSTOMER_NAME': 'Users', 'Company_Code': 'Name', 'Country_Code': 'Company', 'INVOICED_QUANTITY': 'QTY'}, axis = 1, inplace = True)
        c5.rename_axis(None, axis = 1, inplace = True)
        c5.rename_axis(None, axis = 0, inplace = True)
        c5.set_index('Users', inplace = True)
        c5 = c5.style.background_gradient(cmap = 'Greys', axis = None, low = 0.75, high = 1.0)
        ## Exporting the Data
        dfi.export(c3, 'AlertReportGeneration_v1/resources/plots/{}/c3_{}.png'.format(company_code, part_no))
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C3 : PROCESSED')
        dfi.export(c5, 'AlertReportGeneration_v1/resources/plots/{}/c5_{}.png'.format(company_code, part_no))
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C5 : PROCESSED')
        
    def p5(company_code, part_no, doc_id):
        ## c6 c7
        c6_c7 = pd.read_sql("select * from sc_report10_fc_data where company_code = '{}' and part_no = '{}' and doc_id = {} order by 5, 6".format(company_code, part_no, doc_id), con = connection)
        year_no = c6_c7['YEAR_NO'].max()
        ## c6
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C6 : PROCESSING')
        c6 = c6_c7[c6_c7['YEAR_NO'] == year_no]
        c6 = c6[['DATA_FLAG', 'MONTH_1', 'MONTH_2', 'MONTH_3', 'MONTH_4', 'MONTH_5', 'MONTH_6', 'MONTH_7', 'MONTH_8', 'MONTH_9', 'MONTH_10', 'MONTH_11', 'MONTH_12']]
        c6.columns = c6.iloc[:1,:].values[0].tolist()
        c6 = c6.iloc[1:, :].set_index('Heading')
        c6.rename_axis(None, axis = 1, inplace = True)
        c6.rename_axis(None, axis = 0, inplace = True)
        c6 = c6.style.background_gradient(cmap = 'Greys', axis = None, low = 0.75, high = 1.0)
        ## c7
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C7 : PROCESSING')
        c7 = c6_c7[c6_c7['YEAR_NO'] == (year_no - 1)]
        c7 = c7[['DATA_FLAG', 'MONTH_1', 'MONTH_2', 'MONTH_3', 'MONTH_4', 'MONTH_5', 'MONTH_6', 'MONTH_7', 'MONTH_8', 'MONTH_9', 'MONTH_10', 'MONTH_11', 'MONTH_12']]
        c7.columns = c7.iloc[:1,:].values[0].tolist()
        c7 = c7.iloc[1:, :].set_index('Heading')
        c7.rename_axis(None, axis = 1, inplace = True)
        c7.rename_axis(None, axis = 0, inplace = True)
        c7 = c7.style.background_gradient(cmap = 'Greys', axis = None, low = 0.75, high = 1.0)
        ## Exporting the Data
        dfi.export(c6, 'AlertReportGeneration_v1/resources/plots/{}/c6_{}.png'.format(company_code, part_no))
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C6 : PROCESSED')
        dfi.export(c7, 'AlertReportGeneration_v1/resources/plots/{}/c7_{}.png'.format(company_code, part_no))
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C7 : PROCESSED')
        return year_no
        
    def p6(company_code, part_no):
        ## c8
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C8 : PROCESSING')
        c8 = pd.read_sql("select * from sc_report10_breakdown where company_code = '{}' and part_no = '{}'".format(company_code, part_no), con = connection).iloc[:, 2:]
        c8.rename({'SEQ_NO': 'No', 'BOM_PART': 'Part', 'BOM_QTY': 'QTY', 'STOCK': 'Stock', 'ANALYSIS': 'Analysis'}, axis = 1, inplace = True)
        c8.set_index('No', inplace = True)
        c8.rename_axis(None, axis = 0, inplace = True)
        c8 = c8.style.background_gradient(cmap = 'Greys', axis = None, low = 0.75, high = 1.0)
        ## c9
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C9 : PROCESSING')
        c9 = pd.read_sql("select * from sc_report10_wh where company_code = '{}' and part_no = '{}'".format(company_code, part_no), con = connection).iloc[:, 2:]
        c9.rename({'SEQ_NO': 'No', 'WH_CODE': 'Warehouse', 'QTY_STOCK': 'QTY', 'QTY_RSV': 'RSV', 'QTY_IN': 'IN', 'QTY_ICT': 'ICT', 'QTY_OUT': 'OUT', 'QTY_OCT': 'OCT'}, axis = 1, inplace = True)
        c9.set_index('No', inplace = True)
        c9.rename_axis(None, axis = 0, inplace = True)
        c9 = c9.style.background_gradient(cmap = 'Greys', axis = None, low = 0.75, high = 1.0)
        ## Exporting the Data
        dfi.export(c8, 'AlertReportGeneration_v1/resources/plots/{}/c8_{}.png'.format(company_code, part_no))
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C8 : PROCESSED')
        dfi.export(c9, 'AlertReportGeneration_v1/resources/plots/{}/c9_{}.png'.format(company_code, part_no))
        print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part_no, ':', company_code, ': C9 : PROCESSED')
        
    if __name__ == '__main__':
        ccode = '95018'
        curr = connection.cursor() 
        report_path = os.path.join(os.getcwd(), 'AlertReportGeneration_v1', 'reports', ccode)
        Path(report_path).mkdir(parents = True, exist_ok = True)
        in_company_param_data = pd.read_sql("select * from in_company_param where company_code = '{}'".format(ccode), con = connection)
        #last_sale_date, out1, out2 = int(dt.strftime(dt.strptime(str(in_company_param_data['LAST_SALE_DATE'].values[0]), '%Y-%m-%dT%H:%M:%S.%f000'), '%Y%m%d')), int(), int()
        last_sale_date, out1, out2 = '20220331', int(), int()
        sc_alert_data = pd.read_sql("select * from sc_alert_data where company_code = '{}' and doc_id = '{}'".format(ccode, last_sale_date), con = connection)
        parts = sc_alert_data['PART_NO'].tolist()
        for part in parts[:1]:
            print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT : CREATING REPORT FOR : ', part, ' : ', ccode,)
            plot_path = os.path.join(os.getcwd(), 'AlertReportGeneration_v1', 'resources', 'plots', ccode)
            Path(plot_path).mkdir(parents = True, exist_ok = True)
            hist_py_fc_data_new_data = pd.read_sql("select * from hist_py_fc_data_new where company_code = '{}' and part_no = '{}' order by 1".format(ccode, part), con = connection).iloc[-1:,:]
            sc_alert_data_part = sc_alert_data[sc_alert_data['PART_NO'] == part] 
            period_flag = sc_alert_data_part['PERIOD_FLAG'].values[0]
            reason = sc_alert_data_part['FLAG_DESC'].values[0]
            output = curr.callproc('GET_PERIOD_RANGE', [last_sale_date, period_flag, out1, out2])
            start, end = int(output[2]), int(output[3])
            ## D5
            region, abbr, period_catg, forecast_comp, forecast_ytd, actual_ytd, forecast_catg, perc_dev, selected_method = in_company_param_data['REGION'].values[0], in_company_param_data['COMPANY_ABBR'].values[0], hist_py_fc_data_new_data['PERIOD_CATG'].values[0], hist_py_fc_data_new_data['YR_FC'].values[0], hist_py_fc_data_new_data['YTD_FC'].values[0], hist_py_fc_data_new_data['YTD_ACT'].values[0], hist_py_fc_data_new_data['FC_TYPE'].values[0], hist_py_fc_data_new_data['PCNT_CHANGE'].values[0], hist_py_fc_data_new_data['METHOD_NAME'].values[0]        
            p1(ccode, part)
            p2(ccode, part, start, end)
            p3(ccode, part, start)
            p4(ccode, part)
            p6(ccode, part)
            # pool = mp.Pool(processes = 5)
            # plots = {'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p6': p6}
            # for plot in plots:
            #     if plot == 'p2':
            #         pool.apply_async(plots[plot], args = (ccode, part, start, end), callback = None)
            #     elif plot == 'p3':
            #         pool.apply_async(plots[plot], args = (ccode, part, start), callback = None)
            #     else:
            #         pool.apply_async(plots[plot], args = (ccode, part), callback = None)
            # pool.close()
            # pool.join()
            year = p5(ccode, part, last_sale_date)
            class PDF(FPDF):
                def header(self):
                    # Logo
                    self.image('AlertReportGeneration_v1/resources/logo/smc.png', 10, 5, 15)
                    self.image('AlertReportGeneration_v1/resources/logo/analytics.jpg', 187.3, 2.5, 13.5)
                    # Arial bold 15
                    self.set_font('Arial', 'B', 12)
                    # Move to the right
                    #self.cell(63)
                    self.cell(0, h = 5, txt = '', ln = 1)
                    # Title
                    self.cell(0, h = 7, txt = 'Forecasting Analysis', align = 'C', fill = True)
                    # Line break
                    self.ln(5)
            
            print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part, ':', ccode, ': WRITING REPORT')
            pdf = PDF(orientation = 'P', unit = 'mm', format = 'A4')
            pdf.alias_nb_pages()
            pdf.set_fill_color(r = 204, g = 204, b = 204)
            pdf.set_draw_color(r = 204, g = 204, b = 204)
            pdf.add_page()
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, h = 1, ln = 1)
            pdf.cell(0, h = 9, txt = 'Company Code: {}'.format(ccode), align = 'L')
            pdf.cell(0, h = 9, txt = 'Alert No: {}'.format('ASFKNSJKFN#$#%#$!$WQ'), align = 'R', ln = 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, h = 5, txt = "This Alert is generated from SCM system for Part '{}'. Please observe the undersigned analysis for efficient Inventory Management.  According to the Prediction and Analysis, part '{}' will have '{}' in the future. Please find further details below.".format(part, part, 'GROWTH'), align = 'L')
            pdf.set_draw_color(r = 0, g = 0, b = 0)
            pdf.cell(123)
            pdf.multi_cell(0, h = 2, txt = '', align = 'L')
            pdf.cell(123)
            pdf.multi_cell(0, h = 5, txt = "Reason for alert : '{}'".format(reason), align = 'L', border = 1)
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c1_{}.png".format(ccode, part), 10, 47, 122, 62)
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c2_{}.png".format(ccode, part), 10, 110, 122, 62)
            pdf.set_font('Arial', 'U', 10)
            pdf.cell(123)
            pdf.multi_cell(0, h = 9, txt = 'Historical Actual Sale and Order', align = 'C')
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c3_{}.png".format(ccode, part), 133, 65, 68, 16)
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c4_{}.png".format(ccode, part), 133, 82, 68, 67)
            pdf.cell(0, h = 81, ln = 1)
            pdf.cell(123)
            pdf.multi_cell(0, h = 9, txt = 'Top 5 Sales Users', align = 'C')
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c5_{}.png".format(ccode, part), 133, 155, 68, 30)
            pdf.cell(123, h = 15, ln = 1)
            pdf.cell(123, h = 9, txt = 'Information about part {} for {}'.format(part, year), align = 'C', ln = 1)
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c6_{}.png".format(ccode, part), 10, 179, 121, 34)
            pdf.cell(123, h = 6, ln = 1)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Company Code : {}'.format(ccode), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Abbreviation : {}'.format(abbr), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Region Code : {}'.format(region), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Period Category : {}'.format(period_catg), align = 'L', ln = 1)
            pdf.set_font('Arial', 'U', 10)
            pdf.cell(123, h = 6, txt = 'Information about part {} for {}'.format(part, (year - 1)), align = 'C')
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c7_{}.png".format(ccode, part), 10, 220, 121, 34.5)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, h = 7, txt = 'Forecast (Complete) : {}'.format(forecast_comp), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Forecast (YTD) : {}'.format(forecast_ytd), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Actual (YTD) : {}'.format(actual_ytd), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Forecast Category : {}'.format(forecast_catg), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Percentage Deviation : {} %'.format(perc_dev), align = 'L', ln = 1)
            pdf.cell(123, h = 0)
            pdf.cell(0, h = 7, txt = 'Selected Method : {}'.format(selected_method), align = 'L', ln = 1)
            pdf.set_font('Arial', 'U', 10)
            pdf.cell(77, h = 4, txt = 'Part Break Down List', align = 'C')
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c8_{}.png".format(ccode, part), 10, 261, 75, 29)
            pdf.cell(141, h = 4, txt = 'Warehouses Stock situation ({}/{})'.format(str(end)[:4], str(end)[-2:]), align = 'C')
            pdf.image("AlertReportGeneration_v1/resources/plots/{}/c9_{}.png".format(ccode, part), 110, 261, 90, 29)
            ## Exporting the pdf
            try:
                pdf.output('AlertReportGeneration_v1/reports/{}/{}_ForecastingReport.pdf'.format(ccode, part), 'F')
            except Exception as exp:
                ## Printing the log
                print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT :', part, ':', ccode, ': EXCEPTION OCCURED WHILE CREATING THE REPORT :', exp)
            ## Printing the log
            print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT : REPORT GENERATED FOR : {} : COMPANY CODE : {}                                                     '.format(part, ccode))
            shutil.rmtree(plot_path)
        ## Closing the Database connection
        connection.close()                    

except ValueError:
    ## Printing the log
    print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT : EXCEPTION OCCURRED WHILE CONNECTING TO DB')
    
except Exception as main_exp:
    ## Printing the log
    print('[', dt.today().date(), '] [', dt.today().time(), '] : PART ALERT REPORT : EXCEPTION OCCURED :', main_exp)
    ## Closing the Database connection
    connection.close()