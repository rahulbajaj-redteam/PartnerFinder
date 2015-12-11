# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 16:52:21 2015

@author: rbajaj
"""
from __future__ import print_function
import MySQLdb
import string
import mysql.connector
from app import app
import numpy as np
from .SearchForm import SearchForm
import pandas as pd            
from pandas import DataFrame
from flask import Flask , request, render_template, Response,redirect,jsonify,make_response,session
import re, json
import collections
from datetime import date
import math
import csv
import pandasql as pdsql

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'



@app.route('/gdrive',methods=['GET'])
def gdrive():
    records = getGdriveData()
    x= DataFrame(records)
    pendingReports = DataFrame(getGdrivePending())
    
    variable = []
    for j in range(0,len(x.ix[:,:])):
        variable.append([ str('<a href ="') + str(x.ix[j,0]) + str('">') + str(filter(lambda x: x in string.printable, x.ix[j,1])) + str('</a>'),  str( x.ix[j,2]),  str(filter(lambda x: x in string.printable, x.ix[j,3]))   ,  str(filter(lambda x: x in string.printable, x.ix[j,6]))  , str(x.ix[j,5])])            

    Pending_variable = []

    for j in range(0,len(pendingReports.ix[:,:])):
        Pending_variable.append([str(filter(lambda x: x in string.printable, pendingReports.ix[j,0]))])            
    return render_template('gdrive.html', title='Red Hat : GDrive', df=variable,dfpending = Pending_variable)
                               








# index view function suppressed for brevity
@app.route('/index')
@app.route('/', methods= ['GET', 'POST'])
@app.route('/reset', methods= ['GET', 'POST'])
def home():
    query = ''
    form = SearchForm(csrf_enabled=False)
    productFilter = ''
    industryFilter = ''
    prod_req = str(form.prod_req.data)
    session['prod_req'] = prod_req
    ind_req = str(form.ind_req.data)
    session['ind_req'] = ind_req
    region_req = str(form.region_req.data)
    country_req = str(form.country_req.data)
    name_req = str(form.name_req.data)
    role_req = str(form.role_req.data)
    level_req = str(form.level_req.data)            
    CISCO_Partner_req = request.form.getlist('CISCOPartner')
    CITRIX_Partner_req = request.form.getlist('CITRIXPartner')
    MS_Partner_req = request.form.getlist('MSPartner')
    Dell_Partner_req = request.form.getlist('DellPartner')
    IBM_Partner_req = request.form.getlist('IBMPartner')
    Oracle_Partner_req = request.form.getlist('OraclePartner')
    VM_Partner_req = request.form.getlist('VMPartner')
    RH_Partner_req = str(form.RH_Partner_req.data)
    SAP_Partner_req = request.form.getlist('SAPPartner')
    Global_Partner_req = form.Global_Partner_req.data       
    session['prod_req'] = prod_req
    session['ind_req'] = ind_req
    session['region_req'] = region_req
    session['country_req'] = country_req
    session['name_req'] = name_req
    session['role_req'] = role_req
    session['level_req'] = level_req
    session['RH_Partner_req'] = RH_Partner_req
    session['Global_Partner_req'] = Global_Partner_req
    session['CISCO_Partner_req'] = CISCO_Partner_req
    session['CITRIX_Partner_req'] = CITRIX_Partner_req
    session['MS_Partner_req'] = MS_Partner_req
    session['Dell_Partner_req'] = Dell_Partner_req
    session['IBM_Partner_req'] = IBM_Partner_req
    session['Oracle_Partner_req'] = Oracle_Partner_req
    session['VM_Partner_req'] = VM_Partner_req
    session['SAP_Partner_req'] = SAP_Partner_req      
    
    
    if prod_req != 'Any':
        productFilter = getProductFilter(prod_req)
        query = query + str(productFilter)
    if ind_req != 'Any' :
        industryFilter = getIndustryFilter(ind_req)
        if len(query)<5:
            query = query + str(industryFilter)
        else:
            query = str(query) + ' and ' +  str(industryFilter)
    if region_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoRegion = "' + str(region_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoRegion = "' + str(region_req) + '"'
    if country_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoCountry = "' + str(country_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoCountry = "' + str(country_req) + '"'
    if name_req != '' :
        if len(query)<5:
            query = query + ' Name like "%' + str(name_req) + '%" '
        else:
            query = str(query) + ' and ' +   ' Name like "%' + str(name_req) + '%" '        
    if role_req != 'Any' :
        roleFilter = getRoleFilter(role_req)
        if len(query)<5:
            query = query + str(roleFilter)
        else:
            query = str(query) + ' and ' +  str(roleFilter)  
            
    if level_req != 'Any' :
        levelFilter = getlevelFilter(level_req)
        if len(query)<5:
            query = query + str(levelFilter)
        else:
            query = str(query) + ' and ' +  str(levelFilter)  

            
    query = setPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req,RH_Partner_req)
    if len(query) > 2:    
        x= getPartners(query)
    else: 
        x= getPartners('')
    x= getPartners(query)
    x= DataFrame(x)
    x = x.reset_index()
    x = x.ix[:,1:]
    nrows = len(x.index)
    variable = []
    geo = [['Lat', 'Long', 'Name']]
    for j in range(0,len(x.ix[:,:])):
        variable.append([str(filter(lambda x: x in string.printable, x.ix[j,0])).upper() + str('<BR>') + str('<a href = /PWeb/') + str(x.ix[j,3]) + str('  target = "_blank" >WebSite</a>') + str('&nbsp;&nbsp;|&nbsp;&nbsp;<a href="PDetails/') + str(x.ix[j,4]) + str('" target = "_blank" > Details</a>') ])
        try:
            lat = float(str(x.ix[j,5])[1:str(x.ix[j,5]).find(',')-1])
            long =float(str(x.ix[j,5])[str(x.ix[j,5]).find(',')+1:len(str(x.ix[j,5]))-1])
            geo.append([lat,long,str(filter(lambda x: x in string.printable, x.ix[j,0])).upper()])      
        except:
            pass
    return render_template('result.html', title='Red Hat : Partner Finder', df=variable,query=str(query),form=form,geoData=geo,nrows=nrows,Cisco_dummy = CISCO_Partner_req,CITRIX_dummy = CITRIX_Partner_req,MS_dummy = MS_Partner_req,Dell_dummy = Dell_Partner_req,IBM_dummy = IBM_Partner_req,Oracle_dummy = Oracle_Partner_req,VM_dummy = VM_Partner_req,SAP_dummy = SAP_Partner_req,RH_dummy = RH_Partner_req)
                               














# index view function suppressed for brevity
@app.route('/search', methods=['GET', 'POST'])
@app.route('/graphview', methods=['GET', 'POST'])
def search():

    query = ''
    form = SearchForm(csrf_enabled=False)
    productFilter = ''
    industryFilter = ''
    prod_req = ''
    ind_req = ''
    region_req=''
    country_req = ''
    name_req = ''
    role_req = ''
    level_req = ''
    CISCO_Partner_req = ''
    CITRIX_Partner_req = ''
    MS_Partner_req = ''
    Dell_Partner_req = ''
    IBM_Partner_req = ''
    Oracle_Partner_req = ''
    VM_Partner_req = ''
    RH_Partner_req = ''
    SAP_Partner_req = ''
    Global_Partner_req = ''
    prod_req = str(form.prod_req.data)
    ind_req = str(form.ind_req.data)
    region_req = str(form.region_req.data)
    country_req = str(form.country_req.data)
    name_req = str(form.name_req.data)
    role_req = str(form.role_req.data)
    level_req = str(form.level_req.data)
    RH_Partner_req = str(form.RH_Partner_req.data)
    Global_Partner_req = form.Global_Partner_req.data                
    CISCO_Partner_req = request.form.getlist('CISCOPartner')
    CITRIX_Partner_req = request.form.getlist('CITRIXPartner')
    MS_Partner_req = request.form.getlist('MSPartner')
    Dell_Partner_req = request.form.getlist('DellPartner')
    IBM_Partner_req = request.form.getlist('IBMPartner')
    Oracle_Partner_req = request.form.getlist('OraclePartner')
    VM_Partner_req = request.form.getlist('VMPartner')      
    SAP_Partner_req = request.form.getlist('SAPPartner')
     
    session['prod_req'] = prod_req
    session['ind_req'] = ind_req
    session['region_req'] = region_req
    session['country_req'] = country_req
    session['name_req'] = name_req
    session['role_req'] = role_req
    session['level_req'] = level_req
    session['RH_Partner_req'] = RH_Partner_req
    session['Global_Partner_req'] = Global_Partner_req
    session['CISCO_Partner_req'] = CISCO_Partner_req
    session['CITRIX_Partner_req'] = CITRIX_Partner_req
    session['MS_Partner_req'] = MS_Partner_req
    session['Dell_Partner_req'] = Dell_Partner_req
    session['IBM_Partner_req'] = IBM_Partner_req
    session['Oracle_Partner_req'] = Oracle_Partner_req
    session['VM_Partner_req'] = VM_Partner_req
    session['SAP_Partner_req'] = SAP_Partner_req


    
    if prod_req != 'Any':
        productFilter = getProductFilter(prod_req)
        query = query + str(productFilter)
    if ind_req != 'Any' :
        industryFilter = getIndustryFilter(ind_req)
        if len(query)<5:
            query = query + str(industryFilter)
        else:
            query = str(query) + ' and ' +  str(industryFilter)
    if region_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoRegion = "' + str(region_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoRegion = "' + str(region_req) + '"'
    if country_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoCountry = "' + str(country_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoCountry = "' + str(country_req) + '"'
    if name_req != '' :
        if len(query)<5:
            query = query + ' Name like "%' + str(name_req) + '%" '
        else:
            query = str(query) + ' and ' +   ' Name like "%' + str(name_req) + '%" '        
    if role_req != 'Any' :
        roleFilter = getRoleFilter(role_req)
        if len(query)<5:
            query = query + str(roleFilter)
        else:
            query = str(query) + ' and ' +  str(roleFilter)  
            
    if level_req != 'Any' :
        levelFilter = getlevelFilter(level_req)
        if len(query)<5:
            query = query + str(levelFilter)
        else:
            query = str(query) + ' and ' +  str(levelFilter)  

            
    query = setPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req,RH_Partner_req)
    if len(query) > 2:    
        x= getPartners(query)
    else: 
        x= getPartners('')
    x= getPartners(query)
    x= DataFrame(x)
    x = x.reset_index()
    x = x.ix[:,1:]

    nrows = len(x.index)
    variable = []
    geo = [['Lat', 'Long', 'Name']]
    for j in range(0,len(x.ix[:,:])):
        variable.append([str(filter(lambda x: x in string.printable, x.ix[j,0])).upper() + str('<BR>') + str('<a href = /PWeb/') + str(x.ix[j,3]) + str('  target = "_blank" >WebSite</a>') + str('&nbsp;&nbsp;|&nbsp;&nbsp;<a href="PDetails/') + str(x.ix[j,4]) + str('" target = "_blank" > Details</a>') ])
        try:
            lat = float(str(x.ix[j,5])[1:str(x.ix[j,5]).find(',')-1])
            long =float(str(x.ix[j,5])[str(x.ix[j,5]).find(',')+1:len(str(x.ix[j,5]))-1])
            geo.append([lat,long,str(filter(lambda x: x in string.printable, x.ix[j,0])).upper()])      
        except:
            pass
    return render_template('result.html', title='Red Hat : Partner Finder', df=variable,query=str(query),form=form,geoData=geo,nrows=nrows,Cisco_dummy = CISCO_Partner_req,CITRIX_dummy = CITRIX_Partner_req,MS_dummy = MS_Partner_req,Dell_dummy = Dell_Partner_req,IBM_dummy = IBM_Partner_req,Oracle_dummy = Oracle_Partner_req,VM_dummy = VM_Partner_req,SAP_dummy = SAP_Partner_req,RH_dummy = RH_Partner_req)
                               


@app.route('/ToggleRH1/<id>' , methods=['GET', 'POST'])
def ToggleRH1(id):    

    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    cursor = cnx.cursor()
    update_query = "update RHPartners.pttv1 set RH_Partner_Match_Flag = 1 , RH_Partner_ID = 'CorrectedByUser',RH_Partner =1  where id = CONCAT('', %s, '');"
    cursor.execute(update_query,(str(id),))
    cnx.commit()              

    df = getPartnerDetail(id)
    TabOutput = getAssociationDetails(id)
    Comp   = getCompAssociationDetails(id)
    Attr = getPAttributes(id)
    Industry = ''
    Business_Process_Outsourcing_Partner_Flag =''
    Global_Partner_Flag=''
    Service_Partner_Flag=''
    
    Service_Partner_Flag = str(Attr['Services_Partner'].iloc[0])
    Global_Partner_Flag = str(Attr['Global_Partner'].iloc[0])
    Business_Process_Outsourcing_Partner_Flag = str(Attr['Business_Process_Outsourcing_Partner'].iloc[0])
    Industry = ''
    if int(Attr['Ind_Banking'].iloc[0]) > 0:
        Industry = Industry + 'Banking'
    elif Attr['Ind_Computer_Services'].iloc[0] >0:
        Industry = Industry + 'Computer Services'
    elif Attr['Ind_Education'].iloc[0] >0:
        Industry = Industry + 'Education'
    elif Attr['Ind_Electronics'].iloc[0] >0:
        Industry = Industry + 'Electronics'
    elif Attr['Ind_Energy&Utilities'].iloc[0] >0:
        Industry = Industry + 'Energy&Utilities'
    elif Attr['Ind_FinancialMarkets'].iloc[0] >0:
        Industry = Industry + 'Financial Markets'
    elif Attr['Ind_Public_Sector'].iloc[0] >0:
        Industry = Industry + 'Public Sector'
    elif Attr['Ind_Healthcare'].iloc[0] >0:
        Industry = Industry + 'Healthcare'
    elif Attr['Ind_IndustrialProducts'].iloc[0] >0:
        Industry = Industry + 'Industrial Products'
    elif Attr['Ind_Insurance'].iloc[0] >0:
        Industry = Industry + 'Insurance'
    elif Attr['Ind_ProfessionalServices'].iloc[0] >0:
        Industry = Industry + 'Professional Services'
    elif Attr['Ind_Retail'].iloc[0] >0:
        Industry = Industry + 'Retail'
    elif Attr['Ind_Telecommunications'].iloc[0] >0:
        Industry = Industry + 'Telecommunications'
    elif Attr['Ind_WholesaleDistribution&Services'].iloc[0] >0:
        Industry = Industry + 'Wholesale Distribution & Services'
    elif Attr['Ind_Automotive'].iloc[0] >0:
        Industry = Industry + 'Automotive'
    elif Attr['Ind_ConsumerProducts'].iloc[0] >0:
        Industry = Industry + 'Consumer Products'
    elif Attr['Ind_Travel&Transportation'].iloc[0] >0:
        Industry = Industry + 'Travel & Transportation'
    elif Attr['Ind_Media&Entertainment'].iloc[0] >0:
        Industry = Industry + 'Media & Entertainment'
    elif Attr['Ind_Chemicals&Petroleum'].iloc[0] >0:
        Industry = Industry + 'Chemicals & Petroleum'
    elif Attr['Ind_LifeSciences'].iloc[0] >0:
        Industry = Industry + 'Life Sciences'
    elif Attr['Ind_Aerospace&Defense'].iloc[0] >0:
        Industry = Industry + 'Aerospace & Defense'
    elif Attr['Ind_EngineeringandConstruction'].iloc[0] >0:
        Industry = Industry + 'Engineering and Construction'            
        
    Overview = str(df['Overview'].iloc[0])
    Overview = str(Overview)[0:Overview.find("', u")]
    ToggleBtn = ''
    if str(df['RH_Partner'].iloc[0]) == '1':
        ToggleBtn = str('<a href = /ToggleRH0/') + str(id) + str('  target = "_blank" >Not a Red Hat Partner</a>')
    else:
        ToggleBtn = str('<a href = /ToggleRH1/') + str(id) + str('  target = "_blank" >Its a Red Hat Partner</a>')
    return render_template('PDetails.html', title='Red Hat : Partner Finder', name=str(df['Name'].iloc[0]),url = str('<a href = ') +str(df['Partner_Url'].iloc[0])  + str('  target = "_blank" >') +  str(df['Partner_Url'].iloc[0]) + str('</a>'),email1=str(df['Email1'].iloc[0]),email2=str(df['Email2'].iloc[0]), AD1=str(df['Addr_Line1'].iloc[0]), AD2=str(df['Addr_Line2'].iloc[0]), AD3=str(df['Addr_Line3'].iloc[0]), AD_City=str(df['Addr_City'].iloc[0]), AD_State=str(df['Addr_State'].iloc[0]), AD_Country=str(df['GeoCountry'].iloc[0]), AD_Region=str(df['GeoRegion'].iloc[0]) , AD_Phone1=str(df['Phone1'].iloc[0]),  AD_Fax=str(df['Fax'].iloc[0]), Overview =Overview ,  YearEstablished = str(df['YearEstablished'].iloc[0]), RHP=str(df['RH_Partner'].iloc[0]), Comp = str(Comp),Industry = Industry , Business_Process_Outsourcing_Partner_Flag=Business_Process_Outsourcing_Partner_Flag,Global_Partner_Flag=str(Attr['Global_Partner'].iloc[0]), Service_Partner_Flag=Service_Partner_Flag,TabOutput=str(TabOutput), ToggleBtn = str(ToggleBtn),id=str(id) )





@app.route('/ToggleRH0/<id>' , methods=['GET', 'POST'])
def ToggleRH0(id):
    try:
        cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
        cursor = cnx.cursor()
        update_query = "update RHPartners.pttv1 set RH_Partner_Match_Flag = 0 , RH_Partner =0  where id = CONCAT('', %s, '')"
        cursor.execute(update_query,(str(id),))
        cnx.commit()

    except Exception:
        pass
    finally:
        df = getPartnerDetail(id)
        TabOutput = getAssociationDetails(id)
        Comp   = getCompAssociationDetails(id)
        Attr = getPAttributes(id)
        Industry = ''
        Business_Process_Outsourcing_Partner_Flag =''
        Global_Partner_Flag=''
        Service_Partner_Flag=''
        
        Service_Partner_Flag = str(Attr['Services_Partner'].iloc[0])
        Global_Partner_Flag = str(Attr['Global_Partner'].iloc[0])
        Business_Process_Outsourcing_Partner_Flag = str(Attr['Business_Process_Outsourcing_Partner'].iloc[0])
        Industry = ''
        if int(Attr['Ind_Banking'].iloc[0]) > 0:
            Industry = Industry + 'Banking'
        elif Attr['Ind_Computer_Services'].iloc[0] >0:
            Industry = Industry + 'Computer Services'
        elif Attr['Ind_Education'].iloc[0] >0:
            Industry = Industry + 'Education'
        elif Attr['Ind_Electronics'].iloc[0] >0:
            Industry = Industry + 'Electronics'
        elif Attr['Ind_Energy&Utilities'].iloc[0] >0:
            Industry = Industry + 'Energy&Utilities'
        elif Attr['Ind_FinancialMarkets'].iloc[0] >0:
            Industry = Industry + 'Financial Markets'
        elif Attr['Ind_Public_Sector'].iloc[0] >0:
            Industry = Industry + 'Public Sector'
        elif Attr['Ind_Healthcare'].iloc[0] >0:
            Industry = Industry + 'Healthcare'
        elif Attr['Ind_IndustrialProducts'].iloc[0] >0:
            Industry = Industry + 'Industrial Products'
        elif Attr['Ind_Insurance'].iloc[0] >0:
            Industry = Industry + 'Insurance'
        elif Attr['Ind_ProfessionalServices'].iloc[0] >0:
            Industry = Industry + 'Professional Services'
        elif Attr['Ind_Retail'].iloc[0] >0:
            Industry = Industry + 'Retail'
        elif Attr['Ind_Telecommunications'].iloc[0] >0:
            Industry = Industry + 'Telecommunications'
        elif Attr['Ind_WholesaleDistribution&Services'].iloc[0] >0:
            Industry = Industry + 'Wholesale Distribution & Services'
        elif Attr['Ind_Automotive'].iloc[0] >0:
            Industry = Industry + 'Automotive'
        elif Attr['Ind_ConsumerProducts'].iloc[0] >0:
            Industry = Industry + 'Consumer Products'
        elif Attr['Ind_Travel&Transportation'].iloc[0] >0:
            Industry = Industry + 'Travel & Transportation'
        elif Attr['Ind_Media&Entertainment'].iloc[0] >0:
            Industry = Industry + 'Media & Entertainment'
        elif Attr['Ind_Chemicals&Petroleum'].iloc[0] >0:
            Industry = Industry + 'Chemicals & Petroleum'
        elif Attr['Ind_LifeSciences'].iloc[0] >0:
            Industry = Industry + 'Life Sciences'
        elif Attr['Ind_Aerospace&Defense'].iloc[0] >0:
            Industry = Industry + 'Aerospace & Defense'
        elif Attr['Ind_EngineeringandConstruction'].iloc[0] >0:
            Industry = Industry + 'Engineering and Construction'            
            
        Overview = str(df['Overview'].iloc[0])
        Overview = str(Overview)[0:Overview.find("', u")]
        ToggleBtn = ''
        if str(df['RH_Partner'].iloc[0]) == '1':
            ToggleBtn = str('<a href = /ToggleRH0/') + str(id) + str('  target = "_blank" >Not a Red Hat Partner</a>')
        else:
            ToggleBtn = str('<a href = /ToggleRH1/') + str(id) + str('  target = "_blank" >Its a Red Hat Partner</a>')
        return render_template('PDetails.html', title='Red Hat : Partner Finder', name=str(df['Name'].iloc[0]),url = str('<a href = ') +str(df['Partner_Url'].iloc[0])  + str('  target = "_blank" >') +  str(df['Partner_Url'].iloc[0]) + str('</a>'),email1=str(df['Email1'].iloc[0]),email2=str(df['Email2'].iloc[0]), AD1=str(df['Addr_Line1'].iloc[0]), AD2=str(df['Addr_Line2'].iloc[0]), AD3=str(df['Addr_Line3'].iloc[0]), AD_City=str(df['Addr_City'].iloc[0]), AD_State=str(df['Addr_State'].iloc[0]), AD_Country=str(df['GeoCountry'].iloc[0]), AD_Region=str(df['GeoRegion'].iloc[0]) , AD_Phone1=str(df['Phone1'].iloc[0]),  AD_Fax=str(df['Fax'].iloc[0]), Overview =Overview ,  YearEstablished = str(df['YearEstablished'].iloc[0]), RHP=str(df['RH_Partner'].iloc[0]), Comp = str(Comp),Industry = Industry , Business_Process_Outsourcing_Partner_Flag=Business_Process_Outsourcing_Partner_Flag,Global_Partner_Flag=str(Attr['Global_Partner'].iloc[0]), Service_Partner_Flag=Service_Partner_Flag,TabOutput=str(TabOutput), ToggleBtn = str(ToggleBtn),id=str(id) ,uq= str(update_query))













@app.route('/PDetails/<id>' , methods=['GET', 'POST'])
def PDetails(id):
    df = getPartnerDetail(id)
    TabOutput = getAssociationDetails(id)
    #Comp   = getCompAssociationDetails(id)
    Attr = getPAttributes(id)
    Industry = ''
    Business_Process_Outsourcing_Partner_Flag =''
    #Global_Partner_Flag=''
    Service_Partner_Flag=''
    
    Service_Partner_Flag = str(Attr['Services_Partner'].iloc[0])
    #Global_Partner_Flag = str(Attr['Global_Partner'].iloc[0])
    Business_Process_Outsourcing_Partner_Flag = str(Attr['Business_Process_Outsourcing_Partner'].iloc[0])
    Industry = ''
    if int(Attr['Ind_Banking'].iloc[0]) > 0:
        Industry = Industry + 'Banking'
    elif Attr['Ind_Computer_Services'].iloc[0] >0:
        Industry = Industry + 'Computer Services'
    elif Attr['Ind_Education'].iloc[0] >0:
        Industry = Industry + 'Education'
    elif Attr['Ind_Electronics'].iloc[0] >0:
        Industry = Industry + 'Electronics'
    elif Attr['Ind_Energy&Utilities'].iloc[0] >0:
        Industry = Industry + 'Energy&Utilities'
    elif Attr['Ind_FinancialMarkets'].iloc[0] >0:
        Industry = Industry + 'Financial Markets'
    elif Attr['Ind_Public_Sector'].iloc[0] >0:
        Industry = Industry + 'Public Sector'
    elif Attr['Ind_Healthcare'].iloc[0] >0:
        Industry = Industry + 'Healthcare'
    elif Attr['Ind_IndustrialProducts'].iloc[0] >0:
        Industry = Industry + 'Industrial Products'
    elif Attr['Ind_Insurance'].iloc[0] >0:
        Industry = Industry + 'Insurance'
    elif Attr['Ind_ProfessionalServices'].iloc[0] >0:
        Industry = Industry + 'Professional Services'
    elif Attr['Ind_Retail'].iloc[0] >0:
        Industry = Industry + 'Retail'
    elif Attr['Ind_Telecommunications'].iloc[0] >0:
        Industry = Industry + 'Telecommunications'
    elif Attr['Ind_WholesaleDistribution&Services'].iloc[0] >0:
        Industry = Industry + 'Wholesale Distribution & Services'
    elif Attr['Ind_Automotive'].iloc[0] >0:
        Industry = Industry + 'Automotive'
    elif Attr['Ind_ConsumerProducts'].iloc[0] >0:
        Industry = Industry + 'Consumer Products'
    elif Attr['Ind_Travel&Transportation'].iloc[0] >0:
        Industry = Industry + 'Travel & Transportation'
    elif Attr['Ind_Media&Entertainment'].iloc[0] >0:
        Industry = Industry + 'Media & Entertainment'
    elif Attr['Ind_Chemicals&Petroleum'].iloc[0] >0:
        Industry = Industry + 'Chemicals & Petroleum'
    elif Attr['Ind_LifeSciences'].iloc[0] >0:
        Industry = Industry + 'Life Sciences'
    elif Attr['Ind_Aerospace&Defense'].iloc[0] >0:
        Industry = Industry + 'Aerospace & Defense'
    elif Attr['Ind_EngineeringandConstruction'].iloc[0] >0:
        Industry = Industry + 'Engineering and Construction'            
        
    Overview = str(df['Overview'].iloc[0])
    Overview = str(Overview)[0:Overview.find("', u")]
    ToggleBtn = ''
    if str(df['RH_Partner'].iloc[0]) == '1':
        ToggleBtn = str('<a href = /ToggleRH0/') + str(id) + str('  target = "_blank" >Not a Red Hat Partner</a>')
    else:
        ToggleBtn = str('<a href = /ToggleRH1/') + str(id) + str('  target = "_blank" >Its a Red Hat Partner</a>')
    return render_template('PDetails.html', title='Red Hat : Partner Finder', name=str(df['Name'].iloc[0]),url = str('<a href = ') +str(df['Partner_Url'].iloc[0])  + str('  target = "_blank" >') +  str(df['Partner_Url'].iloc[0]) + str('</a>'),email1=str(df['Email1'].iloc[0]),email2=str(df['Email2'].iloc[0]), AD1=str(df['Addr_Line1'].iloc[0]), AD2=str(df['Addr_Line2'].iloc[0]), AD3=str(df['Addr_Line3'].iloc[0]), AD_City=str(df['Addr_City'].iloc[0]), AD_State=str(df['Addr_State'].iloc[0]), AD_Country=str(df['GeoCountry'].iloc[0]), AD_Region=str(df['GeoRegion'].iloc[0]) , AD_Phone1=str(df['Phone1'].iloc[0]),  AD_Fax=str(df['Fax'].iloc[0]), Overview =Overview ,  YearEstablished = str(df['YearEstablished'].iloc[0]), RHP=str(df['RH_Partner'].iloc[0]),Industry = Industry , Business_Process_Outsourcing_Partner_Flag=Business_Process_Outsourcing_Partner_Flag,Global_Partner_Flag=str(Attr['Global_Partner'].iloc[0]), Service_Partner_Flag=Service_Partner_Flag,TabOutput=str(TabOutput), ToggleBtn = str(ToggleBtn),id=str(id) )
    





def getAssociationDetails(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT VMWare_Partner_ID,MS_Partner_ID,SAP_Partner_ID,Oracle_Partner_ID,Dell_Partner_ID,Citrix_Partner_ID,RH_Partner_ID,IBM_Partner_ID,Cisco_Partner_ID  from rhpartners.pttv1 where id =" + id +" ;"
    data = pd.read_sql(query,cnx)    
    cnx.close()
    if data is None:
        return "Username or Password is wrong"
    
    htmlText = ''
    

#    if data['RH_Partner_ID'].iloc[0] != '' :
#        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>Red Hat</b></font></td> <td>')
#        htmlText = htmlText + '-' + '</td><td>' # Product & Services
#        htmlText = htmlText + '-' + '</td><td>' # Specialization
#        htmlText = htmlText + '-' +  str('</td><td>') # Certification
#        htmlText = htmlText +   '-'  + str('</td> <td>') # Authorization
#        htmlText = htmlText +  '-'   + str('</td></tr>') # Partnership Level

    if data['Cisco_Partner_ID'].iloc[0] != '' :
        CDet = getCiscoAssDet(id)
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>Cisco</b></font></td> <td>')
        htmlText = htmlText +   str(CDet[4]) + '</td><td>' # Product & Services
        htmlText = htmlText + str(CDet[0])[3:len(str(CDet[0]))-2] + '</td><td>' # Specialization
        htmlText = htmlText +   '-' + '</td><td>' # Certification
        
        
        htmlText = htmlText +  str('<ul><li>') + str(CDet[1]) + str('</li></ul>') + str('</td> <td>') # Authorization
        if len(str(CDet[3]))>1:    
            htmlText = htmlText + "<b>Category : </b><br/>" + str(CDet[3]) + '<br/><br/>'  # Partnership Level
        if len(str(CDet[2]))>1:
            htmlText = htmlText + '<b>Partners Since :</b><br/>'+  str(CDet[2])
            
        htmlText = htmlText + str('</td></tr>') 
            
    if data['Citrix_Partner_ID'].iloc[0] != '' :
        CDet = getCitrixAssDet(id)
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>Citrix</b></font></td> <td>')
        htmlText = htmlText + "<b>Products Certified to Sell : </b><br><ul>" + str(CDet[3]).replace("Citrix","</li><li>Citrix") + '</td><td>' # Product & Services
        if len(str(CDet[4]))>5:    
            htmlText = htmlText + "<b>Industry Served : </b><br>" + str(CDet[4])+'</td><td>' # Specialization
        else:
            htmlText = htmlText + "-" + '</td><td>' # Specialization
        Citrix_Certifications_Held_by_Staff = ''
        if len(str(CDet[6])[31:])>1:            
            Citrix_Certifications_Held_by_Staff = "<br/><b>Citrix_Certifications_Held_by_Staff : </b><br>" +str(CDet[6])[:31]+ "<ul><li>" + str(CDet[6])[31:].replace(")",")</li><li>")  
            
        htmlText = htmlText +  "<b>Certification Count : </b>" + str(CDet[2])  + "<br/>" +str(Citrix_Certifications_Held_by_Staff)[:len(str(Citrix_Certifications_Held_by_Staff))-9] +  str('</td><td>') # Certification
        if len(str(CDet[5]))>1:    
            htmlText = htmlText +  "<b>Services Offered : </b><br/><ul><li>" + str(CDet[5]).replace("|","</li><li>")[:-4]  + str('</ul></td> <td>') # Authorization
        else:
            htmlText = htmlText +  "-"  + str('</td> <td>') # Authorization
        
        if int(CDet[7])>0:
            htmlText = htmlText + "<b>Role : </b><br/>" + str(CDet[1]) + "<br/><br/><b>Category : </b><br/>" + str(CDet[0]) + "<br/><br/><b>Partner Since : </b>" + str(2015 - int(CDet[7]) ) + str('</td></tr>') # Partnership Level
        else:
            htmlText = htmlText + "<b>Role : </b><br/>" + str(CDet[1]) + "<br/><br/><b>Category : </b>" + str(CDet[0]) +  str('</td></tr>') # Partnership Level



    if data['Dell_Partner_ID'].iloc[0] != '' :
        CDet = getDellAssDet(id)
        Relationship = ''
        Competencies = ''
        if CDet[2]:            
            if len(str(CDet[2]))>4:
                Relationship = str("</br></br><br><b>Relationship : </b>") + str(CDet[2])
                
        if CDet[1]:            
            if len(str(CDet[1]))>4:
                Competencies = str("</br></br><b>Competencies : </b>") + str(CDet[1])

                
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>Dell</b></font></td> <td>')
        htmlText = htmlText + '-' + '</td><td>' # Product & Services
        htmlText = htmlText + Competencies + '</td><td>' # Specialization
        htmlText = htmlText + '-' +  str('</td><td>') # Certification
        htmlText = htmlText +   '-'  + str('</td> <td>') # Authorization
        htmlText = htmlText +  Relationship   + str('</td></tr>') # Partnership Level


    if data['IBM_Partner_ID'].iloc[0] != '' :
        prodList = getIBMProdDet(id)
        certList = getIBMCertDet(id)
        PType = getIBMPTypeAreaDet(id)
        SolnArea = getIBMSolnAreaDet(id)
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>IBM</b></font></td> <td>')
        if len(SolnArea)>32:    
            htmlText = htmlText + SolnArea + '</td><td>' # Product & Services
        else:
            htmlText = htmlText + '</td><td>'
        htmlText = htmlText + '-' + '</td><td>' # Specialization
        htmlText = htmlText + certList +  str('</td><td>') # Certification
        htmlText = htmlText +   prodList  + str('</td> <td>') # Authorization
        if len(PType)>30:    
            htmlText = htmlText +  PType   + str('</td></tr>') # Partnership Level
        else:
            htmlText = htmlText    + str('</td></tr>') # Partnership Level
            
            
    if data['MS_Partner_ID'].iloc[0] != '' :
        CDet = getMSAssDet(id)
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>Microsoft</b></font></td> <td>')
        htmlText = htmlText + str("<b>Applications : </b><ul><li>") + str(CDet[1]).replace("|","</li><li>") + '</ul><BR/>' + str("<br><b>Services : </b><ul><li>") + str(CDet[3]).replace("|","</li><li>") + '</td><td>' # Product & Services
        htmlText = htmlText + str("<b>Competencies : </b><ul><li>") + str(CDet[2]).replace("|","</li><li>") + '</td><td>' # Specialization
        htmlText = htmlText + '-' +  str('</td><td>') # Certification
        htmlText = htmlText +   '-'  + str('</td> <td>') # Authorization
        htmlText = htmlText +   "<b>Average Rating : </b>" + str(CDet[0])   + str('</td></tr>') # Partnership Level

        

        
    if data['Oracle_Partner_ID'].iloc[0] != '' :
        CDet = getOracleAssDet(id)
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>Oracle</b></font></td> <td>')
        htmlText = htmlText + '-' + '</td><td>' # Product & Services
        if len(str(CDet[2]))>1:
            htmlText = htmlText + "<b>Advance Specialization Applications : </b>" + str(CDet[2]) + '<br/><br>' 
        if len(str(CDet[7]))  >1:  
            htmlText = htmlText + "<b>Active Specialization Applications : </b>" + str(CDet[7]) # Specialization
        htmlText = htmlText +'</td><td>'
        htmlText = htmlText + '-' +  str('</td><td>') # Certification
        htmlText = htmlText +   '-'  + str('</td> <td>') # Authorization
        htmlText = htmlText + "<b>Category : </b><br/>" + str(CDet[0])    + str('</td></tr>') # Partnership Level

      


    if data['SAP_Partner_ID'].iloc[0] != '' :
        CDet = getSAPAssDet(id)
        Specs = '-'
        if CDet[4]:            
            if len(str(CDet[4]))>4:
                Specs = str('<b>SAP Partner Focus Area & Recognised Expertise</b><br>')+ cleanList(str(CDet[4]))
            else:
                Specs = '-'
        # SAP_Engagement,SAP_Type,SAP_Level,SAP_SolnAuth,SAP_FocusArea_RecognisedExpertise,SAP_IndFocus
        htmlText = htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>SAP</b></font></td> <td>')
        if len(str(CDet[3]))   > 5:     
            htmlText = htmlText+ "<b>SAP Solutions : </b><br/>"  + cleanList(str(CDet[3]))   +'</td><td>' # Product & Services
        else:
            htmlText = htmlText+ str('-')    +'</td><td>' # Product & Services
        htmlText = htmlText + str(Specs) + '</td><td>' # Specialization
        htmlText = htmlText + '-' +  str('</td><td>') # Certification
        htmlText = htmlText +   cleanList(str(CDet[0])) + "<br><br>" +  str('</td> <td>') # Authorization
        if len(str(CDet[1]))>3:
            htmlText = htmlText + "<b>Role : </b><br/>" + cleanList(str(CDet[1]))  
        if len(str(CDet[2]))>3:
            htmlText = htmlText + "<br><b>Category : </b>" + str(CDet[2])  
        htmlText = htmlText + str('</td></tr>') # Partnership Level




    if data['VMWare_Partner_ID'].iloc[0] != '' :
        CDet = getVMWareAssDet(id)
        htmlText =  htmlText + str('<tr><td bgcolor="#000000"><font color="#fff"><b>VMWare</b></font></td> <td>')
        htmlText = htmlText + '-' + '</td><td>' # Product & Services
        if len(str(CDet[1]))>5:    
            htmlText = htmlText + "<b>Solution Competency : </b>" + str(CDet[1])  + '</td><td>' # Specialization
        else:    
            htmlText = htmlText + "-" + str('')  + '</td><td>' # Specialization
        htmlText = htmlText + str("<b>VMware Certified Professionals : </b>") + str(CDet[4]) + str("<br><br><b>VMware Technical Solutions Professionals : </b>") + str(CDet[5]) + str("<br><br><b>VMware Sales Professionals : </b>") + str(CDet[6])+ str("<br><br><b>VSPCPs : </b>") + str(CDet[7]) +  str("<br><br><b>VMware Operations Professionals : </b>") + str(CDet[8]) + str("<br><br><b>Total Reseller VLEs : </b>") + str(CDet[9]) +  str("<br><br><b>Total Disti VLEs : </b>") + str(CDet[10]) + str('</td><td>') # Certification
        htmlText = htmlText +   '-'  + str('</td> <td>') # Authorization
        htmlText = htmlText + "<b>Category : </b><br/>"  + str(CDet[2])   + str('</td></tr>') # Partnership Level

       
    return htmlText











def getPAttributes(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Services_Partner,Global_Partner,Business_Process_Outsourcing_Partner,Ind_Banking,Ind_Computer_Services,Ind_Education,Ind_Electronics,`Ind_Energy&Utilities`,Ind_FinancialMarkets,Ind_Public_Sector,Ind_Healthcare,Ind_IndustrialProducts,Ind_Insurance,Ind_ProfessionalServices,Ind_Retail,Ind_Telecommunications,`Ind_WholesaleDistribution&Services`,Ind_Automotive,Ind_ConsumerProducts,`Ind_Media&Entertainment`,`Ind_Travel&Transportation`,`Ind_Chemicals&Petroleum`,Ind_LifeSciences,`Ind_Aerospace&Defense`,`Ind_EngineeringandConstruction`  from rhpartners.pttv1 where id =" + id +" ;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return "Username or Password is wrong"
    return data
    




def getPartnerDetail(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Name,GeoCountry,GeoRegion,Partner_Url,id,RH_Partner_ID,RH_Partner_Tier,Addr_Line1,Addr_Line2,Addr_Line3,Addr_City,Addr_State,Addr_PostCode,Phone1,Phone1_Extn,Phone2,Fax,Email1,Email2,Overview,YearEstablished,RH_Partner  from rhpartners.pttv1 where id =" + id +" ;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return "Username or Password is wrong"
    return data








def getIBMProdDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT IBM_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    IBM_Id = ''
    while row is not None:
        IBM_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT CONCAT(`Brand`, '-', `ProductorService`) AS 'Brand_Product', Role from ibm_partner_product  where id like '" + IBM_Id +"' ;"
    
    ibm_partner_product=pd.read_sql(query, cnx)
    cnx.close()
    prodlist = ibm_partner_product.Role.unique().tolist()
    result_list = ''
    for i in prodlist:
        result_list = result_list + '<b>' + str(i) + '</b>' + cleanList(str(list(ibm_partner_product.Brand_Product[ibm_partner_product.Role == i]))) 
    return result_list



def getIBMSolnAreaDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT IBM_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    IBM_Id = ''
    while row is not None:
        IBM_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT SolutionArea from ibm_partner_solutionarea  where id like '" + IBM_Id +"' ;"
    
    SolutionAreapd=pd.read_sql(query, cnx)
    cnx.close()
    SolnArealist = SolutionAreapd.SolutionArea.unique().tolist()
    result_list = '<b>Solution Area :</b><ul>'
    for i in SolnArealist:
        result_list = result_list + '<li>' + str(i) + '</li>' 
    result_list = result_list + '</ul>'
    return result_list






def getIBMPTypeAreaDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT IBM_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    IBM_Id = ''
    while row is not None:
        IBM_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT BusinessPartnerType from ibm_partner_type  where id like '" + IBM_Id +"' ;"
    
    ibm_partnertype =pd.read_sql(query, cnx)
    cnx.close()
    PTypelist = ibm_partnertype.BusinessPartnerType.unique().tolist()
    result_list = '<b>Partner Type :</b><ul>'
    for i in PTypelist:
        result_list = result_list + '<li>' + str(i) + '</li>' 
    result_list = result_list + '</ul>'
    return result_list







def getIBMCertDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT IBM_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    IBM_Id = ''
    while row is not None:
        IBM_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT CONCAT(`Brand`, '-', `ProductorService`) AS 'Brand_Product', Certification from ibm_partner_certifications  where id like '" + IBM_Id +"' ;"
    
    ibm_partner_cert=pd.read_sql(query, cnx)
    cnx.close()
    Brand_Productlist = ibm_partner_cert.Brand_Product.unique().tolist()
    result_list = ''
    for i in Brand_Productlist:
        result_list = result_list + '<b>' + str(i) + '</b>' + cleanList(str(list(ibm_partner_cert.Certification[ibm_partner_cert.Brand_Product == i]))) 
    return result_list
    
    
    


def cleanList(listItem):
    cleanedList = '<ul>' + str(listItem)
    cleanedList = str(cleanedList).replace("u'","<li>")
    cleanedList = str(cleanedList).replace("',","</li>")
    cleanedList = str(cleanedList).replace("[","")
    cleanedList = str(cleanedList).replace("]","")
    cleanedList = str(cleanedList)[:-1]
    cleanedList = cleanedList + '</ul>'
    return cleanedList







def getSAPAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT SAP_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    SAP_Id = ''
    while row is not None:
        SAP_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT SAP_Engagement,SAP_Type,SAP_Level,SAP_SolnAuth,SAP_FocusArea_RecognisedExpertise,SAP_IndFocus FROM rhpartners.sap_partners where SAP_partner_link like '%" + SAP_Id +"%' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row










def getDellAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Dell_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    Dell_Id = ''
    while row is not None:
        Dell_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT `dell_partnerdetails`.`PartnerId`,`dell_partnerdetails`.`Competencies`,`dell_partnerdetails`.`Relationship`    FROM `rhpartners`.`dell_partnerdetails` where PartnerId like '" + Dell_Id +"' LIMIT 1 ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row









def getVMWareAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT VMWare_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    VMWare_Id = ''
    while row is not None:
        VMWare_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT DISTINCT VMWare_Partner_ID,SolutionCompetency,Level,PartnerProgram,TotalVCPs,TotalVTSPs,TotalVSPs,TotalVSPCPs,TotalVOPs,TotalResellerVLEs,TotalDistiVLEs FROM rhpartners.vmwareportal_partnerdata where VMWare_Partner_ID like '" + VMWare_Id +"' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row
    






def getOracleAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Oracle_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    Oracle_Id = ''
    while row is not None:
        Oracle_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT Partner_Membership_Level,Partner_Employees,Advance_Specializations_Applications,Advance_Specializations_Cloud_Services,Advance_Specializations_Database,Advance_Specializations_Middleware,Advance_Specializations_Server_And_Storage_Systems,Active_Specializations_Applications,Active_Specializations_Cloud_Services,Active_Specializations_Database,Active_Specializations_Middleware,Active_Specializations_Server_And_Storage_Systems,Active_Specializations_Engineered_Systems   from rhpartners.oracle_partnerdata where Partner_ID like '" + Oracle_Id +"' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row
    





def getMSAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT MS_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    MS_Id = ''
    while row is not None:
        MS_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT Avg_Rating,Applications,Competencies,Services   from rhpartners.ms2_partners where ms_partner_id like '" + MS_Id +"' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row
    







def getCiscoAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Cisco_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    Cisco_Id = ''
    while row is not None:
        Cisco_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT Specializations,Other_Authorizations,PartnersSince,Certifications,cloudMangedServices   from rhpartners.cisco_partners where cisco_partner_id like '" + Cisco_Id +"' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row
    



def getCitrixAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Citrix_Partner_Id  from rhpartners.pttv1 where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    Citrix_Id = ''
    while row is not None:
        Citrix_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT Citrix_Partnership_Level,Citrix_Partner_Type, Citrix_Cert_Count, Citrix_Products_Certified_to_Sell,Citrix_Industries_Served,Citrix_Services_Offered,Citrix_Certifications_Held_by_Staff, Citrix_Partnership_Age   from rhpartners.citrixportal_partnerdata2 where Citrix_PID like '" + Citrix_Id +"%' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row






@app.route('/mapview' , methods=['GET', 'POST'])
def mapview():

    form = SearchForm(csrf_enabled=False)
    query = ''
    productFilter = ''
    industryFilter = ''
    prod_req = str(form.prod_req.data)
    ind_req = str(form.ind_req.data)
    region_req = str(form.region_req.data)
    country_req = str(form.country_req.data)
    name_req = str(form.name_req.data)
    role_req = str(form.role_req.data)
    level_req = str(form.level_req.data)
    RH_Partner_req = str(form.RH_Partner_req.data)
    Global_Partner_req = form.Global_Partner_req.data                
    CISCO_Partner_req = request.form.getlist('CISCOPartner')
    CITRIX_Partner_req = request.form.getlist('CITRIXPartner')
    MS_Partner_req = request.form.getlist('MSPartner')
    Dell_Partner_req = request.form.getlist('DellPartner')
    IBM_Partner_req = request.form.getlist('IBMPartner')
    Oracle_Partner_req = request.form.getlist('OraclePartner')
    VM_Partner_req = request.form.getlist('VMPartner')      
    SAP_Partner_req = request.form.getlist('SAPPartner')
     
    session['prod_req'] = prod_req
    session['ind_req'] = ind_req
    session['region_req'] = region_req
    session['country_req'] = country_req
    session['name_req'] = name_req
    session['role_req'] = role_req
    session['level_req'] = level_req
    session['RH_Partner_req'] = RH_Partner_req
    session['Global_Partner_req'] = Global_Partner_req
    session['CISCO_Partner_req'] = CISCO_Partner_req
    session['CITRIX_Partner_req'] = CITRIX_Partner_req
    session['MS_Partner_req'] = MS_Partner_req
    session['Dell_Partner_req'] = Dell_Partner_req
    session['IBM_Partner_req'] = IBM_Partner_req
    session['Oracle_Partner_req'] = Oracle_Partner_req
    session['VM_Partner_req'] = VM_Partner_req
    session['SAP_Partner_req'] = SAP_Partner_req
    
    
    if prod_req != 'Any':
        productFilter = getProductFilter(prod_req)
        query = query + str(productFilter)
    if ind_req != 'Any' :
        industryFilter = getIndustryFilter(ind_req)
        if len(query)<5:
            query = query + str(industryFilter)
        else:
            query = str(query) + ' and ' +  str(industryFilter)
    if region_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoRegion = "' + str(region_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoRegion = "' + str(region_req) + '"'
    if country_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoCountry = "' + str(country_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoCountry = "' + str(country_req) + '"'
    if name_req != '' :
        if len(query)<5:
            query = query + ' Name like "%' + str(name_req) + '%" '
        else:
            query = str(query) + ' and ' +   ' Name like "%' + str(name_req) + '%" '        
    if role_req != 'Any' :
        roleFilter = getRoleFilter(role_req)
        if len(query)<5:
            query = query + str(roleFilter)
        else:
            query = str(query) + ' and ' +  str(roleFilter)   
            
            
    if level_req != 'Any' :
        levelFilter = getlevelFilter(level_req)
        if len(query)<5:
            query = query + str(levelFilter)
        else:
            query = str(query) + ' and ' +  str(levelFilter) 

    query = setPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req,RH_Partner_req)
    NonRHQuery =     setNonRHPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req)
    if len(query) > 2:    
        x= getPartnersLoc(query)
    else: 
        x= getPartnersLoc('') 
    x= getPartnersLoc(query)
    x= DataFrame(x)  
    variable = []
    variable.append([ 'Country' , 'Partners'  ])
    for j in range(0,len(x.ix[:,:])):
        variable.append([str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  x.ix[j,1] ])   
        
    BarJson = getBubbleJson(country_req)
    ORingJson = getORingJson(country_req)
    IRingJson = getIRingJson(country_req)
    x = getBubbleList()
    x = pd.DataFrame(x)
    BubbleList = []
    BubbleList.append([ 'Country_Code','Diamond_Gold_Partners_Count','AverageRating','Country','PartnerCount' ])
    
    for j in range(0,len(x.ix[:,:])):
        BubbleList.append([  str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  x.ix[j,1]  ,  x.ix[j,2] ,  str(filter(lambda x: x in string.printable, x.ix[j,3])) ,  x.ix[j,4]  ])      


    DonutList = getDonutList(query)

    x = getRegionRHPartnerBarData(getRegionRHPartnerBarData,region_req)
    x = pd.DataFrame(x)
    x=x[0::]
    BarList = []
    ColumnBarList = []  
    ColumnBarListJson = ''
      
    BarList.append(['Region','RHPartner','NonRHPartner'])

    try:
        
        for j in range(0,len(x.ix[:,:])):
            if x.shape[1]==2:
               x.ix[j,2] = 0 
            BarList.append([  str(x.ix[j,0]) ,  int(x.ix[j,1])  ,  int(x.ix[j,2])  ])      
       
    
        x = getRegionProdRHBarData(query,region_req)
        x = pd.DataFrame(x)
      
        ColumnBarList.append(['Geo','Platforms', 'Virtualization' ,'Cloud' ,'Storage', 'Middleware', 'Analytics' ,'IoT' ,'DataManagement' ,'Mobility' , 'SCM' ,'CRM'])
 
        for j in range(0,len(x.ix[:,:])):
            ColumnBarList.append([  str(x.ix[j,0]) ,  int(x.ix[j,1])  ,  int(x.ix[j,2]) , int(x.ix[j,3])  ,  int(x.ix[j,4]) , int(x.ix[j,5])  ,  int(x.ix[j,6]) , int(x.ix[j,7])  ,  int(x.ix[j,8]) , int(x.ix[j,9])  ,  int(x.ix[j,10]) , int(x.ix[j,11])  ])    
            
        ColumnBarListJson = getRegionProdRHBarDataJson(query,region_req)   
    except:
        pass 
    return render_template('resultmap.html',  title='Sign In',   dfmap=variable,query=str(query),form = form,Cisco_dummy = CISCO_Partner_req,CITRIX_dummy = CITRIX_Partner_req,MS_dummy = MS_Partner_req,Dell_dummy = Dell_Partner_req,IBM_dummy = IBM_Partner_req,Oracle_dummy = Oracle_Partner_req,VM_dummy = VM_Partner_req,SAP_dummy = SAP_Partner_req,RH_dummy = RH_Partner_req,bubble = BarJson, ORingJson = ORingJson, IRingJson = IRingJson,BubbleList = BubbleList,DonutList=DonutList,RegionBarList=BarList,ColumnBarList=ColumnBarList,ColumnBarListJson = ColumnBarListJson)








def getBubbleList():
    cnx = mysql.connector.connect(user='rbajaj', password='nxzd8978',host='localhost',database='rhpartners')
    sql=  "SELECT * from ptt_GeoCountry_NonRH_Gold_Diamond_Partners;"
    NonRH_Gold_Diamond_Partners=pd.read_sql(sql, cnx)
    sql= "SELECT * from ptt_GeoCountry_Avg_Levels;"
    ptt_GeoCountry_Avg_Levels=pd.read_sql(sql, cnx)
    sql=  "SELECT * from ptt_GeoCountry_PartnersCount;"
    ptt_GeoCountry_PartnersCount=pd.read_sql(sql, cnx)
    ptt_GeoCountry_PartnersCount = ptt_GeoCountry_PartnersCount.sort('Count(*)',ascending=False).head(7)
    resultset = pd.DataFrame.merge(ptt_GeoCountry_PartnersCount, ptt_GeoCountry_Avg_Levels, left_on='Country', right_on='GeoCountry', how='inner')
    resultset = pd.DataFrame.merge(resultset, NonRH_Gold_Diamond_Partners, left_on='Country', right_on='GeoCountry', how='inner')
    resultset = resultset.drop(resultset.columns[[3, 5]], axis=1) # Note: zero indexed
    resultset.columns = ['Country_Code','Country','PartnerCount','AverageRating','Diamond_Gold_Partners_Count']
    result = pd.concat([resultset.Country_Code,resultset.Diamond_Gold_Partners_Count,resultset.AverageRating,resultset.Country,resultset.PartnerCount],axis=1)
    return result
    








def getDonutList(queryclause):
    query = "SELECT sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics)as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_CRM) as CRM,sum(Prod_SCM) as SCM,sum(Prod_Security) as Security FROM `rhpartners`.`pttv1`  WHERE RH_Partner = 0 and " + queryclause + ";"
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return ''
    Prod_df = pd.DataFrame(data.transpose())
    Prod_df.index.name = 'Product'
    Prod_df.reset_index(inplace=True)
    Prod_df.values.tolist()
    
    df = pd.DataFrame(Prod_df.values.tolist())
    x = df
    x = pd.DataFrame(x)
    DonutList = []
    DonutList.append([ 'Product','Count' ])
        
    for j in range(0,len(x.ix[:,:])):
        DonutList.append([ str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  x.ix[j,1]   ]) 
    
    return DonutList    








def getBubbleJson(country_req):
    query = 'SELECT GeoCountry,Count(*) AS NumberOfPartners,avg(Avg_Level) as AvgRating , Avg_Level*Count(*) AS NOA from rhpartners.pttv1 '
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    if country_req != 'Any' :
        query = query + ' where GeoCountry = "' + str(country_req) + '"'
        
    query = query + " group by GeoCountry Order by 2 desc LIMIT 7;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return ''
    else:
        d1 = data.to_json()
        d1 = data.to_json(orient='records')
        return d1
      
      
      
      
      
      
        

def getRegionRHPartnerBarData(queryclause,region_req):
    result = DataFrame()
    try:
        
        cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
        if str(queryclause).find('RH_Partner')>0:
                
            if str(queryclause).find('GeoRegion') + str(queryclause).find('GeoCountry') < 0:    
                query = "SELECT GeoRegion,Count(RH_Partner) from  pttv1 Where " + queryclause + " And GeoRegion not like 'Unknown' Group By GeoRegion,RH_Partner;"
                ResultDS_NonRH = pd.read_sql(query,cnx)
                ResultDS_NonRH.columns = ['GeoRegion','NonRH_Partner']
                query = "SELECT GeoRegion,Count(RH_Partner) from  pttv1 Where " + queryclause + " And GeoRegion not like 'Unknown' Group By GeoRegion,RH_Partner;"
                ResultDS_RH = pd.read_sql(query,cnx)
                ResultDS_RH.columns = ['GeoRegion','RH_Partner']
                result=pd.concat([ResultDS_RH.GeoRegion,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)
            elif str(queryclause).find('GeoRegion') > 0 and str(queryclause).find('GeoCountry') < 0:
                query = "Select GeoCountry, count(*) from pttv1 WHERE GeoRegion like '%" + region_req  +"%' And GeoRegion not like 'Unknown' group by GeoCountry order by 2 desc LIMIT 5 ;"
                ResultDS_Country = pd.read_sql(query,cnx)
                ResultDS_Country.columns = ['GeoCountry','Partner']
                Clist = ResultDS_Country.GeoCountry.values.tolist()
                list = ''
                for j in Clist:
                    list = list + "','" + str(j)        
                list = list[2:] + "'"
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where  " + queryclause + " and GeoCountry in (" + str(list) + ") And GeoCountry not like 'Unknown' Group By GeoCountry,RH_Partner;"
                ResultDS_NonRH = pd.read_sql(query,cnx)
                ResultDS_NonRH.columns = ['GeoCountry','NonRH_Partner']
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where  " + queryclause + " and GeoCountry in (" + str(list) + ")  And GeoCountry not like 'Unknown'  Group By GeoCountry,RH_Partner;"
                ResultDS_RH = pd.read_sql(query,cnx)
                ResultDS_RH.columns = ['GeoCountry','RH_Partner']
                result=pd.concat([ResultDS_RH.GeoCountry,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)
            elif str(queryclause).find('GeoCountry') > 0:
                query = "Select GeoCountry, count(*) from pttv1 WHERE " + queryclause  +"  And GeoCountry not like 'Unknown'  group by GeoCountry order by 2 desc LIMIT 5 ;"
                ResultDS_Country = pd.read_sql(query,cnx)
                ResultDS_Country.columns = ['GeoCountry','Partner']
                Clist = ResultDS_Country.GeoCountry.values.tolist()
                list = ''
                for j in Clist:
                    list = list + "','" + str(j)        
                list = list[2:] + "'"
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where  " + queryclause + "  And GeoCountry not like 'Unknown'  Group By GeoCountry,RH_Partner;"
                ResultDS_NonRH = pd.read_sql(query,cnx)
                ResultDS_NonRH.columns = ['GeoCountry','NonRH_Partner']
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where  " + queryclause + "  And GeoCountry not like 'Unknown'  Group By GeoCountry,RH_Partner;"
                ResultDS_RH = pd.read_sql(query,cnx)
                ResultDS_RH.columns = ['GeoCountry','RH_Partner']
                result=pd.concat([ResultDS_RH.GeoCountry,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)
        else:
            if str(queryclause).find('GeoRegion') + str(queryclause).find('GeoCountry') < 0:    
                query = "SELECT GeoRegion,Count(RH_Partner) from  pttv1 Where RH_Partner = 0 and " + queryclause + " And GeoRegion not like 'Unknown' Group By GeoRegion,RH_Partner;"
                ResultDS_NonRH = pd.read_sql(query,cnx)
                ResultDS_NonRH.columns = ['GeoRegion','NonRH_Partner']
                query = "SELECT GeoRegion,Count(RH_Partner) from  pttv1 Where RH_Partner = 1 and " + queryclause + " And GeoRegion not like 'Unknown' Group By GeoRegion,RH_Partner;"
                ResultDS_RH = pd.read_sql(query,cnx)
                ResultDS_RH.columns = ['GeoRegion','RH_Partner']
                result=pd.concat([ResultDS_RH.GeoRegion,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)
            elif str(queryclause).find('GeoRegion') > 0 and str(queryclause).find('GeoCountry') < 0:
                query = "Select GeoCountry, count(*) from pttv1 WHERE GeoRegion like '%" + region_req  +"%' And GeoRegion not like 'Unknown' group by GeoCountry order by 2 desc LIMIT 5 ;"
                ResultDS_Country = pd.read_sql(query,cnx)
                ResultDS_Country.columns = ['GeoCountry','Partner']
                Clist = ResultDS_Country.GeoCountry.values.tolist()
                list = ''
                for j in Clist:
                    list = list + "','" + str(j)        
                list = list[2:] + "'"
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where RH_Partner = 0 and " + queryclause + " and GeoCountry in (" + str(list) + ") And GeoCountry not like 'Unknown' Group By GeoCountry,RH_Partner;"
                ResultDS_NonRH = pd.read_sql(query,cnx)
                ResultDS_NonRH.columns = ['GeoCountry','NonRH_Partner']
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where RH_Partner = 1 and " + queryclause + " and GeoCountry in (" + str(list) + ")  And GeoCountry not like 'Unknown'  Group By GeoCountry,RH_Partner;"
                ResultDS_RH = pd.read_sql(query,cnx)
                ResultDS_RH.columns = ['GeoCountry','RH_Partner']
                result=pd.concat([ResultDS_RH.GeoCountry,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)
            elif str(queryclause).find('GeoCountry') > 0:
                query = "Select GeoCountry, count(*) from pttv1 WHERE " + queryclause  +"  And GeoCountry not like 'Unknown'  group by GeoCountry order by 2 desc LIMIT 5 ;"
                ResultDS_Country = pd.read_sql(query,cnx)
                ResultDS_Country.columns = ['GeoCountry','Partner']
                Clist = ResultDS_Country.GeoCountry.values.tolist()
                list = ''
                for j in Clist:
                    list = list + "','" + str(j)        
                list = list[2:] + "'"
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where RH_Partner = 0 and " + queryclause + "  And GeoCountry not like 'Unknown'  Group By GeoCountry,RH_Partner;"
                ResultDS_NonRH = pd.read_sql(query,cnx)
                ResultDS_NonRH.columns = ['GeoCountry','NonRH_Partner']
                query = "SELECT GeoCountry,Count(RH_Partner) from  pttv1 Where RH_Partner = 1 and " + queryclause + "  And GeoCountry not like 'Unknown'  Group By GeoCountry,RH_Partner;"
                ResultDS_RH = pd.read_sql(query,cnx)
                ResultDS_RH.columns = ['GeoCountry','RH_Partner']
                result=pd.concat([ResultDS_RH.GeoCountry,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)            
    except:
        result = DataFrame()
    cnx.close()
    return result.values.tolist() 








def getProdRHPartnerBarData(queryclause):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT GeoRegion,Count(RH_Partner) from  pttv1 Where RH_Partner = 0 and " + queryclause + " Group By GeoRegion,RH_Partner;"
    ResultDS_NonRH = pd.read_sql(query,cnx)
    ResultDS_NonRH.columns = ['GeoRegion','NonRH_Partner']
    query = "SELECT GeoRegion,Count(RH_Partner) from  pttv1 Where RH_Partner = 1 and " + queryclause + " Group By GeoRegion,RH_Partner;"
    ResultDS_RH = pd.read_sql(query,cnx)
    ResultDS_RH.columns = ['GeoRegion','RH_Partner']
    result=pd.concat([ResultDS_RH.GeoRegion,ResultDS_RH.RH_Partner,ResultDS_NonRH.NonRH_Partner],axis=1)
    cnx.close()
    return result.values.tolist() 




def getRegionProdRHBarDataJson(queryclause,region_req):
    result = []
    try:
        
        cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
        if str(queryclause).find('GeoRegion') + str(queryclause).find('GeoCountry') < 0:    
            str1 = "SELECT GeoRegion as Geo,sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage ,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics) as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_SCM) as SCM, sum(Prod_CRM) as CRM from rhpartners.pttv1 where " + queryclause + " and  GeoRegion not like 'Unknown' and GeoCountry not like 'Unknown' Group By GeoRegion;"
            result = pd.read_sql(str1, cnx)

            
        elif str(queryclause).find('GeoRegion') > 0 and str(queryclause).find('GeoCountry') < 0:
            query = "Select GeoCountry as Geo, count(*) from pttv1 WHERE GeoRegion like '%" + region_req  +"%' And GeoRegion not like 'Unknown' group by GeoCountry order by 2 desc LIMIT 5 ;"
            ResultDS_Country = pd.read_sql(query,cnx)
            ResultDS_Country.columns = ['GeoCountry','Partner']
            Clist = ResultDS_Country.GeoCountry.values.tolist()
            list = ''
            for j in Clist:
                list = list + "','" + str(j)        
            list = list[2:] + "'"
            query = "SELECT GeoCountry as Geo,sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage ,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics) as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_SCM) as SCM, sum(Prod_CRM) as CRM from  pttv1 Where RH_Partner = 0 and " + queryclause + " and GeoCountry in (" + str(list) + ") And GeoCountry not like 'Unknown' Group By GeoCountry;"
            result = pd.read_sql(query,cnx)

        elif str(queryclause).find('GeoCountry') > 0:
            query = "Select GeoCountry as Geo, count(*) from pttv1 WHERE " + queryclause  +"  And GeoCountry not like 'Unknown'  group by GeoCountry order by 2 desc LIMIT 5 ;"
            ResultDS_Country = pd.read_sql(query,cnx)
            ResultDS_Country.columns = ['GeoCountry','Partner']
            Clist = ResultDS_Country.GeoCountry.values.tolist()
            list = ''
            for j in Clist:
                list = list + "','" + str(j)        
            list = list[2:] + "'"
            query = "SELECT GeoCountry as Geo,sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage ,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics) as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_SCM) as SCM, sum(Prod_CRM) as CRM from  pttv1 Where RH_Partner = 0 and " + queryclause + "  And GeoCountry not like 'Unknown'  Group By GeoCountry;"
            result = pd.read_sql(query,cnx)
          
    except:
        result = []
    cnx.close()
    
    
    r = result.transpose()

    res = pd.DataFrame()
    res = pd.concat([res,r[0][1:]],axis=1)
    res[1] = "APAC"
    result  = res
    result.columns = ['PCount', 'Geo']
    
    res = pd.DataFrame(r[1][1:])
    res[2] = "EMEA"
    res.columns = ['PCount', 'Geo']
    result = result.append(res)
    
    
    res = pd.DataFrame(r[2][1:])
    res[1] = "LATAM"
    res.columns = ['PCount', 'Geo']
    result = result.append(res)
    
    res = pd.DataFrame(r[3][1:])
    res[2] = "NA"
    res.columns = ['PCount', 'Geo']
    result = result.append(res)
    
    result.index.name = 'ProductBU'
    result.reset_index(inplace=True)
    result = result.to_json(orient='records')
    return result



def getRegionProdRHBarData(queryclause,region_req):
    result = []
    try:
        
        cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
        if str(queryclause).find('GeoRegion') + str(queryclause).find('GeoCountry') < 0:    
            str1 = "SELECT GeoRegion,sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage ,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics) as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_SCM) as SCM, sum(Prod_CRM) as CRM from rhpartners.pttv1 where " + queryclause + " and  GeoRegion not like 'Unknown' and GeoCountry not like 'Unknown' Group By GeoRegion;"
            result = pd.read_sql(str1, cnx)

            
        elif str(queryclause).find('GeoRegion') > 0 and str(queryclause).find('GeoCountry') < 0:
            query = "Select GeoCountry, count(*) from pttv1 WHERE GeoRegion like '%" + region_req  +"%' And GeoRegion not like 'Unknown' group by GeoCountry order by 2 desc LIMIT 5 ;"
            ResultDS_Country = pd.read_sql(query,cnx)
            ResultDS_Country.columns = ['GeoCountry','Partner']
            Clist = ResultDS_Country.GeoCountry.values.tolist()
            list = ''
            for j in Clist:
                list = list + "','" + str(j)        
            list = list[2:] + "'"
            query = "SELECT GeoCountry,sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage ,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics) as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_SCM) as SCM, sum(Prod_CRM) as CRM from  pttv1 Where RH_Partner = 0 and " + queryclause + " and GeoCountry in (" + str(list) + ") And GeoCountry not like 'Unknown' Group By GeoCountry;"
            result = pd.read_sql(query,cnx)

        elif str(queryclause).find('GeoCountry') > 0:
            query = "Select GeoCountry, count(*) from pttv1 WHERE " + queryclause  +"  And GeoCountry not like 'Unknown'  group by GeoCountry order by 2 desc LIMIT 5 ;"
            ResultDS_Country = pd.read_sql(query,cnx)
            ResultDS_Country.columns = ['GeoCountry','Partner']
            Clist = ResultDS_Country.GeoCountry.values.tolist()
            list = ''
            for j in Clist:
                list = list + "','" + str(j)        
            list = list[2:] + "'"
            query = "SELECT GeoCountry,sum(Prod_Platforms) as Platforms,sum(Prod_Virtualization) as Virtualization,sum(Prod_Cloud) as Cloud ,sum(Prod_Storage) as Storage ,sum(Prod_Middleware) as Middleware,sum(Prod_Analytics) as Analytics,sum(Prod_IoT) as IoT,sum(Prod_DataManagement) as DataManagement,sum(Prod_Mobility) as Mobility,sum(Prod_SCM) as SCM, sum(Prod_CRM) as CRM from  pttv1 Where RH_Partner = 0 and " + queryclause + "  And GeoCountry not like 'Unknown'  Group By GeoCountry;"
            result = pd.read_sql(query,cnx)
          
    except:
        result = []
    cnx.close()
    return result


def getIRingJson(country_req):
    query = 'SELECT Prod_Type,Count from rhpartners.ptt_partner_prod where GeoCountry like "SPAIN";'
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return ''
    else:
        d1 = data.to_json()
        d1 = data.to_json(orient='records')
        return d1
        
        
        
        
        
        
        

def getORingJson(country_req):
    query = 'SELECT sum(Prod_Platforms) as Prod_Platforms,sum(Prod_Virtualization) as Prod_Virtualization,sum(Prod_Cloud) as Prod_Cloud ,sum(Prod_Storage) as Prod_Storage ,sum(Prod_Middleware) as Prod_Middleware,sum(Prod_Analytics) as Prod_Analytics,sum(Prod_IoT) as Prod_IoT,sum(Prod_DataManagement) as Prod_DataManagement,sum(Prod_Mobility) as Prod_Mobility,sum(Prod_SCM) as Prod_SCM, sum(Prod_CRM) as Prod_CRM,sum(Prod_Security) as Prod_Security, sum(Prod_Platforms)+sum(Prod_Virtualization)+sum(Prod_Cloud)+sum(Prod_Storage)+sum(Prod_Middleware)+sum(Prod_Analytics)+sum(Prod_IoT)+sum(Prod_DataManagement)+sum(Prod_Mobility)+sum(Prod_SCM)+ sum(Prod_CRM)+sum(Prod_Security) as total from rhpartners.pttv1 '
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    if country_req != 'Any' :
        query = query + ' where GeoCountry = "' + str(country_req) + '"'        
    query = query + " ;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return ''
    else:
        
        resultset = []
        #resultset.extend([data[0]*100/data['sum'],data[1]*100/data['sum'],data[2]*100/data['sum'],data[3]*100/data['sum'],data[4]*100/data['sum'],data[5]*100/data['sum'],data[6]*100/data['sum'],data[7]*100/data['sum'],data[8]*100/data['sum'],data[9]*100/data['sum'],data[10]*100/data['sum'],data[11]*100/data['sum'],data[12]*100/data['sum']])
        item = 'Product,Count'
        resultset.append(item)
        item = 'Platforms,' + str(math.floor(round(int(data['Prod_Platforms'].iloc[0])*100/data['total'].iloc[0],2))) 
        resultset.append(item)
        item = 'Virtualization,' + str(math.floor(round(int(data['Prod_Virtualization'].iloc[0])*100/data['total'].iloc[0])))
        resultset.append(item)
        item = 'Cloud,' + str(math.floor(round(int(data['Prod_Cloud'].iloc[0])*100/data['total'].iloc[0])))
        resultset.append(item)
        item = 'Storage,' + str(math.floor(round(  int(data['Prod_Storage'].iloc[0])*100/data['total'].iloc[0])))
        resultset.append(item)
        item = 'Middleware,' + str(math.floor(round(int(data['Prod_Middleware'].iloc[0])*100/data['total'].iloc[0])))
        resultset.append(item)
        item = 'Analytics,' + str(math.floor(round(int(data['Prod_Analytics'].iloc[0])*100/data['total'].iloc[0]))) 
        resultset.append(item)
        item = 'IoT,' + str(math.floor(round(int(data['Prod_IoT'].iloc[0])*100/data['total'].iloc[0])))
        #resultset.append( item)
        #resultset.append( math.floor(round(int(data['Prod_DataManagement'].iloc[0])*100/data['total'].iloc[0])))
        #resultset.append( math.floor(round(int(data['Prod_Mobility'].iloc[0])*100/data['total'].iloc[0])))
        #resultset.append( math.floor(round(int(data['Prod_SCM'].iloc[0])*100/data['total'].iloc[0])))
        #resultset.append( math.floor(round(int(data['Prod_CRM'].iloc[0])*100/data['total'].iloc[0])))
        #resultset.append( math.floor(round(int(data['Prod_Security'].iloc[0])*100/data['total'].iloc[0])))
        resultset = pd.DataFrame(resultset)
#        d1 = data.to_json()
#        d1 = data.to_json(orient='records')
        
        return resultset



        



#@app.route('/mapview' , methods=['GET', 'POST'])
@app.route('/tmapview' , methods=['GET', 'POST'])
def tmapview():
    
    form = SearchForm(csrf_enabled=False)
    query = ''
    productFilter = ''
    industryFilter = ''

    prod_req = session['prod_req']
    ind_req = session['ind_req']
    region_req = session['region_req']
    country_req = session['country_req']
    name_req = session['name_req']
    role_req = session['role_req']
    level_req = session['level_req']
    RH_Partner_req = session['RH_Partner_req']
    Global_Partner_req = session['Global_Partner_req']
    CISCO_Partner_req = session['CISCO_Partner_req']
    CITRIX_Partner_req = session['CITRIX_Partner_req']
    MS_Partner_req = session['MS_Partner_req']
    Dell_Partner_req = session['Dell_Partner_req']
    IBM_Partner_req = session['IBM_Partner_req']
    Oracle_Partner_req = session['Oracle_Partner_req']
    VM_Partner_req = session['VM_Partner_req']
    SAP_Partner_req = session['SAP_Partner_req']

    
    if prod_req != 'Any':
        productFilter = getProductFilter(prod_req)
        query = query + str(productFilter)
    if ind_req != 'Any' :
        industryFilter = getIndustryFilter(ind_req)
        if len(query)<5:
            query = query + str(industryFilter)
        else:
            query = str(query) + ' and ' +  str(industryFilter)
    if region_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoRegion = "' + str(region_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoRegion = "' + str(region_req) + '"'
    if country_req != 'Any' :
        if len(query)<5:
            query = query + ' GeoCountry = "' + str(country_req) + '"'
        else:
            query = str(query) + ' and ' +  ' GeoCountry = "' + str(country_req) + '"'
    if name_req != '' :
        if len(query)<5:
            query = query + ' Name like "%' + str(name_req) + '%" '
        else:
            query = str(query) + ' and ' +   ' Name like "%' + str(name_req) + '%" '        
    if role_req != 'Any' :
        roleFilter = getRoleFilter(role_req)
        if len(query)<5:
            query = query + str(roleFilter)
        else:
            query = str(query) + ' and ' +  str(roleFilter)   
            
            
    if level_req != 'Any' :
        levelFilter = getlevelFilter(level_req)
        if len(query)<5:
            query = query + str(levelFilter)
        else:
            query = str(query) + ' and ' +  str(levelFilter) 

    query = setPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req,RH_Partner_req)
        
    if len(query) > 2:    
        x= getPartnersLoc(query)
    else: 
        x= getPartnersLoc('') 
    x= getPartnersLoc(query)
    x= pd.DataFrame(x)  
    variable = []
    variable.append([ 'Country' , 'Partners'  ])
    for j in range(0,len(x.ix[:,:])):
        variable.append([str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  x.ix[j,1] ])      
    
    
    x = getBubbleList()
    x= pd.DataFrame(x)
    BubbleList = []
    BubbleList.append([ 'Country_Code','Country','PartnerCount','AverageRating','Diamond_Gold_Partners_Count' ])
    
    for j in range(0,len(x.ix[:,:])):
        BubbleList.append([  str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  round(x.ix[j,1],2)  ,  round(x.ix[j,2],2)  ,  str(filter(lambda x: x in string.printable, x.ix[j,3])) ,  int(x.ix[j,4])  ])      
    
    return render_template('resultmap.html',  title='Sign In',   dfmap=variable,query=str(query),form = form,Cisco_dummy = CISCO_Partner_req,CITRIX_dummy = CITRIX_Partner_req,MS_dummy = MS_Partner_req,Dell_dummy = Dell_Partner_req,IBM_dummy = IBM_Partner_req,Oracle_dummy = Oracle_Partner_req,VM_dummy = VM_Partner_req,SAP_dummy = SAP_Partner_req,RH_dummy = RH_Partner_req,BubbleList = BubbleList, x = x)



    
@app.route('/graphview', methods=['GET', 'POST'])
def graphview():
    form = SearchForm(csrf_enabled=False)

    return render_template('result.html', form=form )


 



@app.route('/download', methods=['GET', 'POST'])
def download():
    query = ''
    form = SearchForm(csrf_enabled=False)
    productFilter = ''
    industryFilter = ''
    if request.method == 'POST':
        query = ''
        prod_req = str(form.prod_req.data)
        ind_req = str(form.ind_req.data)
        region_req = str(form.region_req.data)
        country_req = str(form.country_req.data)
        name_req = str(form.name_req.data)
        role_req = str(form.role_req.data)
        RH_Partner_req = str(form.RH_Partner_req.data)
        Global_Partner_req = str(form.Gobal_Partner_req.data)              
        CISCO_Partner_req = request.form.getlist('CISCOPartner')
        CITRIX_Partner_req = request.form.getlist('CITRIXPartner')
        MS_Partner_req = request.form.getlist('MSPartner')
        Dell_Partner_req = request.form.getlist('DellPartner')
        IBM_Partner_req = request.form.getlist('IBMPartner')
        Oracle_Partner_req = request.form.getlist('OraclePartner')
        VM_Partner_req = request.form.getlist('VMPartner')      
        SAP_Partner_req = request.form.getlist('SAPPartner')
        if prod_req != 'Any':
            productFilter = getProductFilter(prod_req)
            query = query + str(productFilter)
        if ind_req != 'Any' :
            industryFilter = getIndustryFilter(ind_req)
            if len(query)<5:
                query = query + str(industryFilter)
            else:
                query = str(query) + ' and ' +  str(industryFilter)
        if region_req != 'Any' :
            if len(query)<5:
                query = query + ' GeoRegion = "' + str(region_req) + '"'
            else:
                query = str(query) + ' and ' +  ' GeoRegion = "' + str(region_req) + '"'
        if country_req != 'Any' :
            if len(query)<5:
                query = query + ' GeoCountry = "' + str(country_req) + '"'
            else:
                query = str(query) + ' and ' +  ' GeoCountry = "' + str(country_req) + '"'
        if name_req != '' :
            if len(query)<5:
                query = query + ' Name like "%' + str(name_req) + '%" '
            else:
                query = str(query) + ' and ' +   ' Name like "%' + str(name_req) + '%" '        
        if role_req != 'Any' :
            roleFilter = getRoleFilter(role_req)
            if len(query)<5:
                query = query + str(roleFilter)
            else:
                query = str(query) + ' and ' +  str(roleFilter)  
                
        query = setPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req,RH_Partner_req)
    if len(query) > 2:    
        x= getPartners(query)
    else: 
        x= getPartners('')

    x= getPartners(query)
    x= DataFrame(x)
    
    variable = ""
    for j in range(0,len(x.ix[:,:])):
        variable =variable + str(filter(lambda x: x in string.printable, x.ix[j,0])).upper() + "," + str(filter(lambda x: x in string.printable, x.ix[j,1])) + ',' +  str(x.ix[j,2]) + '\n'
        
    response = make_response(variable)
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response 


@app.route('/PWeb/<url>', methods=['GET', 'POST'])
def PWeb(url):
    return redirect(str("http://")+str(url))





def setPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req,RH_Partner_req):
   
    if CISCO_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Cisco_Partner_Flag = 1 and Cisco_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Cisco_Partner_Flag = 1 and Cisco_Ctry_Partner_Flag = 1' 

    if CITRIX_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Citrix_Partner_Flag = 1 and Citrix_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Citrix_Partner_Flag = 1 and Citrix_Ctry_Partner_Flag = 1' 
    if MS_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' MS_Partner_Flag = 1 and MS_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' MS_Partner_Flag = 1 and MS_Ctry_Partner_Flag = 1' 
                
    if Dell_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Dell_Partner_Flag = 1 and Dell_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Dell_Partner_Flag = 1 and Dell_Ctry_Partner_Flag = 1' 
                
    if IBM_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' IBM_Partner_Flag = 1 and IBM_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' IBM_Partner_Flag = 1 and IBM_Ctry_Partner_Flag = 1' 
                
    if Oracle_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Oracle_Partner_Flag = 1 and Oracle_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Oracle_Partner_Flag = 1 and Oracle_Ctry_Partner_Flag = 1' 


    if VM_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' VMWare_Partner_Flag = 1 and VMWare_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' VMWare_Partner_Flag = 1 and VMWare_Ctry_Partner_Flag = 1' 


    if RH_Partner_req == '1':
         if len(query)<5:
             query = query + " RH_Partner = 1 " 
         else:
             query = str(query) + ' and ' +  "  RH_Partner = 1  " 
                
                
    if RH_Partner_req == '0':
         if len(query)<5:
             query = query +  'RH_Partner != 1'
         else:
             query = str(query) + ' and ' +  'RH_Partner != 1' 


    if SAP_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' SAP_Partner_Flag = 1 and SAP_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' SAP_Partner_Flag = 1 and SAP_Ctry_Partner_Flag = 1' 
             
    if Global_Partner_req:
         if len(query)<5:
             query = query + ' Global_Partner = 1 ' 
         else:
             query = str(query) + ' and  Global_Partner = 1 ' 
    else:
         if len(query)<5:
             query = query + " Global_Partner != 2 " 
         else:
             query = str(query) + " and  Global_Partner != 2 "
        
    return query                  











def setNonRHPartnerFlags(query,CISCO_Partner_req,CITRIX_Partner_req,MS_Partner_req,Dell_Partner_req,IBM_Partner_req,Oracle_Partner_req,VM_Partner_req,SAP_Partner_req,Global_Partner_req):
   
    if CISCO_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Cisco_Partner_Flag = 1 and Cisco_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Cisco_Partner_Flag = 1 and Cisco_Ctry_Partner_Flag = 1' 

    if CITRIX_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Citrix_Partner_Flag = 1 and Citrix_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Citrix_Partner_Flag = 1 and Citrix_Ctry_Partner_Flag = 1' 
    if MS_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' MS_Partner_Flag = 1 and MS_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' MS_Partner_Flag = 1 and MS_Ctry_Partner_Flag = 1' 
                
    if Dell_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Dell_Partner_Flag = 1 and Dell_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Dell_Partner_Flag = 1 and Dell_Ctry_Partner_Flag = 1' 
                
    if IBM_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' IBM_Partner_Flag = 1 and IBM_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' IBM_Partner_Flag = 1 and IBM_Ctry_Partner_Flag = 1' 
                
    if Oracle_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' Oracle_Partner_Flag = 1 and Oracle_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' Oracle_Partner_Flag = 1 and Oracle_Ctry_Partner_Flag = 1' 


    if VM_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' VMWare_Partner_Flag = 1 and VMWare_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' VMWare_Partner_Flag = 1 and VMWare_Ctry_Partner_Flag = 1' 


                


    if SAP_Partner_req == ['1']:
         if len(query)<5:
             query = query + ' SAP_Partner_Flag = 1 and SAP_Ctry_Partner_Flag = 1' 
         else:
             query = str(query) + ' and ' +  ' SAP_Partner_Flag = 1 and SAP_Ctry_Partner_Flag = 1' 
             
    if Global_Partner_req:
         if len(query)<5:
             query = query + ' Global_Partner = 1 ' 
         else:
             query = str(query) + ' and  Global_Partner = 1 ' 
    else:
         if len(query)<5:
             query = query + " Global_Partner != 2 " 
         else:
             query = str(query) + " and  Global_Partner != 2 "
        
    return query                  


                 
                 
                 
def getPartners(queryclause):

    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Name,GeoCountry,GeoRegion,Partner_Url,id,Coordinates from rhpartners.pttv1 "
    
    if len(queryclause)>5:        
        query = query + 'WHERE ' + str(queryclause) + ' Order by id desc LIMIT 250;'     
    else:
        query = query + ' Order by Coordinates desc LIMIT 250 ;'
    data = pd.read_sql(query,cnx)
    
    if data is None:
        return "Username or Password is wrong"
    return data




def getPartnersLoc(queryclause):

    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT GeoCountry,Count(*) AS Count from rhpartners.pttv1 "
    
    if len(queryclause)>5:        
        query = query + 'WHERE ' + str(queryclause) + ' GROUP BY GeoCountry;'     
    else:
        query = query + '  GROUP BY GeoCountry;'
    
    data = pd.read_sql(query,cnx)
    
    if data is None:
        return "Username or Password is wrong"
    return data


def getProductFilter(prod_req):
    if prod_req == 'Analytics':
        return ' Prod_Analytics = 1 '
    elif prod_req == 'Platforms':
        return ' Prod_Platforms = 1 '
    elif prod_req == 'Virtualization':
        return ' Prod_Virtualization = 1 '
    elif prod_req == 'Cloud':
        return ' Prod_Cloud = 1 '
    elif prod_req == 'Storage':
        return ' Prod_Storage = 1 '
    elif prod_req == 'Middleware':
        return ' Prod_Middleware = 1 '
    elif prod_req == 'IoT':
        return ' Prod_IoT = 1 '
    elif prod_req == 'DataManagement':
        return ' Prod_DataManagement = 1 '
    elif prod_req == 'Mobility':
        return ' Prod_Mobility = 1 '
    elif prod_req == 'SCM':
        return ' Prod_SCM = 1 '
    elif prod_req == 'CRM':
        return ' Prod_CRM = 1 '
    elif prod_req == 'Security':
        return ' Prod_Security = 1 ' 
        


        
        
        
def getIndustryFilter(ind_req):
    if ind_req == 'Banking':
        return ' Ind_Banking = 1 '
    else:    
        return ' `Ind_' + str(ind_req) + '` = 1 '


        
        
def getRoleFilter(role_req):
    return ' `Role_' + str(role_req) + '` = 1 '



def getlevelFilter(level_req):
    if level_req == 'Diamond':
        return ' Avg_Level > 3.5 '
    elif level_req == 'Gold':
        return ' Avg_Level > 2.9 and Avg_Level <=3.5 '
    elif level_req == 'Silver':
        return ' Avg_Level > 2.1 and Avg_Level <=2.9 '
    elif level_req == 'Bronze':
        return ' Avg_Level > 1.3 and Avg_Level <=2.1 '
    elif level_req == 'Valued':
        return ' Avg_Level <=1.3 '
    



                 
def getGdriveData():
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT * from gdrive.gdrive ;"
    
    data = pd.read_sql(query,cnx)
    
    if data is None:
        return "Username or Password is wrong"
    return data
    
    
    

def getName():

    Year =''
    if date.today().month > 2:    
        Year = date.today().year + 1 
    else:
        Year = date.today().year
    Year = 'FY' + str(Year)[2:]
        
    Quarter = '' 
    # Get Quarter
    if date.today().month == 3 or date.today().month == 4 or date.today().month == 5:    
        Quarter = 'Q1' 
    elif date.today().month == 6 or date.today().month == 7 or date.today().month == 8:
        Quarter = 'Q2' 
        
    elif date.today().month == 9 or date.today().month == 10 or date.today().month == 11:
        Quarter = 'Q3' 
    else:
        Quarter = 'Q4' 

    # Get Month
#    Month = ''
#    if date.today().month == 3 or date.today().month == 6 or date.today().month == 9 or date.today().month == 12:    
#        Month = 'M1' 
#    elif date.today().month == 4 or date.today().month == 7 or date.today().month == 10 or date.today().month == 1:
#        Month = 'M2'         
#    elif date.today().month == 5 or date.today().month == 8 or date.today().month == 11 or date.today().month == 2:
#        Month = 'M3' 
    return Year + '_' + Quarter + '_' 


def getGdrivePending():
    cnx = mysql.connector.connect(user='rbajaj', password='nxzd8978',  host='localhost', database='RHPartners')
    cursor = cnx.cursor()
    data = ''
    strRecord = ''
    select_query = "SELECT Itemname from gdrive.gdrive"
    
    cursor.execute(select_query)            
    data = cursor.fetchall()
                        
    for record in data:
        strRecord = strRecord +  str(record) + '  '
    
    CoNames= [ 'Cisco Royalty_','Dell Royalty_','IBM Royalty_','Lenovo Royalty_','Stratus Royalty_','Amazon_CCSP Royalty_','CSC_CCSP Royalty_','Dimension Data_CCSP Royalty_','Google CCSP Royalty_','HP ES_CCSP_Royalty_','NaviSite_CCSP Royalty_','Softlayer_CCSP Royalty_']
    CoNamesM = ['IBM_CCSP Royalty_','HP Royalty_']  # no month at the end as they are quarterly
    period = getName()
    pending = []
    for name in CoNames:
        fname1 =  name + period + 'M1'
        fname2 =  name + period + 'M2'
        fname3 =  name + period + 'M3'
        if str(strRecord).find(fname1) > 0:
            pass
        else:
            pending.append(fname1)        
        if str(strRecord).find(fname2) > 0:
            pass
        else:
            pending.append(fname2)
        if str(strRecord).find(fname3) > 0:
            pass
        else:
            pending.append(fname3)

    for name in CoNamesM:
        fname1 =  name + period
        if str(strRecord).find(fname1) > 0:
            pass
        else:
            pending.append(str(fname1)[0:len(fname1)-1])        
            
    return pending
    
    
    
# TODO's
# Partnership level for Dell 
# Address of Partners
# Website linking