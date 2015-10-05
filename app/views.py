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
from sqlalchemy import create_engine 
import pandas as pd            
from pandas import DataFrame
from flask import Flask , request, render_template, Response,redirect,jsonify,make_response,session
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.constants import RAW
from neo4jrestclient.client import Node 
import re, json
from py2neo import neo4j, node, rel 
from py2neo import Graph
from py2neo import authenticate
import collections
from datetime import date


authenticate("localhost:7474", "neo4j", "password")
graph = Graph("http://localhost:7474/db/data/")

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
#
#
#    rule = request.url_rule
#
#
#    try:
#        dummy = id
#    except:
#        dummy =0
#        
#        
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
                               




@app.route('/PDetails/<id>' , methods=['GET', 'POST'])
def PDetails(id):
    df = getPartnerDetail(id)
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
    return render_template('PDetails.html', title='Red Hat : Partner Finder', name=str(df['Name'].iloc[0]),url = str('<a href = ') +str(df['Partner_Url'].iloc[0])  + str('  target = "_blank" >') +  str(df['Partner_Url'].iloc[0]) + str('</a>'),email1=str(df['Email1'].iloc[0]),email2=str(df['Email2'].iloc[0]), AD1=str(df['Addr_Line1'].iloc[0]), AD2=str(df['Addr_Line2'].iloc[0]), AD3=str(df['Addr_Line3'].iloc[0]), AD_City=str(df['Addr_City'].iloc[0]), AD_State=str(df['Addr_State'].iloc[0]), AD_Country=str(df['GeoCountry'].iloc[0]), AD_Region=str(df['GeoRegion'].iloc[0]) , AD_Phone1=str(df['Phone1'].iloc[0]),  AD_Fax=str(df['Fax'].iloc[0]), Overview =Overview ,  YearEstablished = str(df['YearEstablished'].iloc[0]), RHP=str(df['RH_Partner'].iloc[0]), Comp = str(Comp),Industry = Industry , Business_Process_Outsourcing_Partner_Flag=Business_Process_Outsourcing_Partner_Flag,Global_Partner_Flag=str(Attr['Global_Partner'].iloc[0]), Service_Partner_Flag=Service_Partner_Flag )
    


def getPAttributes(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Services_Partner,Global_Partner,Business_Process_Outsourcing_Partner,Ind_Banking,Ind_Computer_Services,Ind_Education,Ind_Electronics,`Ind_Energy&Utilities`,Ind_FinancialMarkets,Ind_Public_Sector,Ind_Healthcare,Ind_IndustrialProducts,Ind_Insurance,Ind_ProfessionalServices,Ind_Retail,Ind_Telecommunications,`Ind_WholesaleDistribution&Services`,Ind_Automotive,Ind_ConsumerProducts,`Ind_Media&Entertainment`,`Ind_Travel&Transportation`,`Ind_Chemicals&Petroleum`,Ind_LifeSciences,`Ind_Aerospace&Defense`,`Ind_EngineeringandConstruction`  from rhpartners.ptt where id =" + id +" ;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return "Username or Password is wrong"
    return data
    




def getPartnerDetail(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Name,GeoCountry,GeoRegion,Partner_Url,id,RH_Partner_ID,RH_Partner_Tier,Addr_Line1,Addr_Line2,Addr_Line3,Addr_City,Addr_State,Addr_PostCode,Phone1,Phone1_Extn,Phone2,Fax,Email1,Email2,Overview,YearEstablished,RH_Partner  from rhpartners.ptt where id =" + id +" ;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return "Username or Password is wrong"
    return data



def getCompAssociationDetails(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT VMWare_Partner_ID,MS_Partner_ID,SAP_Partner_ID,Oracle_Partner_ID,Dell_Partner_ID,Citrix_Partner_ID,RH_Partner_ID,IBM_Partner_ID,Cisco_Partner_ID  from rhpartners.ptt where id =" + id +" ;"
    data = pd.read_sql(query,cnx)    
    cnx.close()
    if data is None:
        return "Username or Password is wrong"
    
    htmlText = ''
    





    if data['Citrix_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>Citrix</h3>  <div>  ")    
        CDet = getCitrixAssDet(id)

        Citrix_PLevel = ''
        if CDet:
            if len(str(CDet[0]))>3 and str(CDet[0]) != 'None':
                Citrix_PLevel = "<b>Partnership Level : </b>" + str(CDet[0])  
                
        Citrix_PType = ''
        if CDet:
            if len(str(CDet[1]))>3 and str(CDet[1]) != 'None':
                Citrix_PType = "<b>Partner Type : </b>" + str(CDet[1])  

        Citrix_CertCount = ''
        if CDet:
            if CDet[2]:
                if CDet[2]>0 and str(CDet[2])!='NA':
                    Citrix_CertCount = "<b>Certification Count : </b>" + str(CDet[2])  
                    
        Citrix_Products_Certified_to_Sell = ''
        if CDet:
            if CDet[3]:
                if len(str(CDet[3]))>4 and str(CDet[3])!='NA':
                    Citrix_Products_Certified_to_Sell = "<br><b>Products Certified to Sell : </b><br><ul>" + str(CDet[3]).replace("Citrix","</li><li>Citrix")  

        Citrix_Services_Offered = ''
        if CDet:
            if CDet[5]:
                if len(str(CDet[5]))>4 and str(CDet[5])!='NA':
                    Citrix_Services_Offered = "<b>Services Offered : </b><br><ul><li>" + str(CDet[5]).replace("|","</li><li>")  
                    Citrix_Services_Offered = str(Citrix_Services_Offered)[:len(str(Citrix_Services_Offered))-9]

        Citrix_Certifications_Held_by_Staff = ''
        if CDet:
            if CDet[6]:
                if len(str(CDet[6]))>4 and str(CDet[6])!='NA':
                    Citrix_Certifications_Held_by_Staff = "<b>Citrix_Certifications_Held_by_Staff : </b><br>" +str(CDet[6])[:31]+ "<ul><li>" + str(CDet[6])[31:].replace(")",")</li><li>")  
                    Citrix_Certifications_Held_by_Staff = str(Citrix_Certifications_Held_by_Staff)[:len(str(Citrix_Certifications_Held_by_Staff))-9]
        
        htmlText =  htmlText + str("") + Citrix_PLevel + Citrix_PType + Citrix_CertCount + Citrix_Products_Certified_to_Sell +str("</ul>")+ Citrix_Services_Offered + str("</ul>") + Citrix_Certifications_Held_by_Staff +  str("</ul></div>")
        
        
    
    if data['Cisco_Partner_ID'].iloc[0] != '' :
        CDet = getCiscoAssDet(id)
        htmlText =  htmlText + str("<h3>Cisco</h3>  <div>    <p> <b> Partners Since : </b>") + str(CDet[2])        
        if len(str(CDet[4]))>5:    
            htmlText =  htmlText + str("<br><br><b>")+ str(CDet[4])[27:] + str("</b></br></br>  <b>Specialization : </b> ") + str(CDet[0])[3:len(str(CDet[0]))-2] + str("</p>  </div>")
        else:
            htmlText =  htmlText + str("   <p>  <b>Specialization : </b> ") + str(CDet[0])[3:len(str(CDet[0]))-2] + str("</p>  </div>")
    
        
    if data['Dell_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>Dell</h3>  <div> ")
        CDet = getDellAssDet(id)  
        Competencies =  ''
        Relationship = ''
        P_Customer = ''
        if CDet[2]:            
            if len(str(CDet[2]))>4:
                Relationship = str("</br></br><br><b>Relationship : </b>") + str(CDet[2])
                
        if CDet[1]:            
            if len(str(CDet[1]))>4:
                Competencies = str("</br></br><b>Competencies : </b>") + str(CDet[1])

        if CDet[3]:            
            if len(str(CDet[3]))>4:
                P_Customer = str("</br></br><b>Primary Customer : </b>") + str(CDet[3])

        htmlText =  htmlText +P_Customer+ Relationship + Competencies + str("  </div>")                                
    if data['IBM_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>IBM</h3>  <div>    <p>IBM Partner </p>  </div>")   





    if data['MS_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>MS</h3><div>")
        CDet = getMSAssDet(id)
        Avg_Rating =  " Rating : "+ CDet[0]

        Applications =''
        if CDet[1]:            
            if len(str(CDet[1]))>4:
                Applications = str("<br><b>Applications : </b><ul><li>") + str(CDet[1]).replace("|","</li><li>")
                
        Competencies =''
        if CDet[2]:            
            if len(str(CDet[2]))>4:
                Competencies = str("<b>Competencies : </b><ul><li>") + str(CDet[2]).replace("|","</li><li>")


        Services =''
        if CDet[3]:            
            if len(str(CDet[3]))>4:
                Services = str("<br><b>Services : </b><ul><li>") + str(CDet[3]).replace("|","</li><li>")
        htmlText =  htmlText + Avg_Rating + Applications + str("</ul>") + Competencies + str("</ul>") + str("  </div>")
        
        
        
    if data['Oracle_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>Oracle</h3>  <div> ")
        CDet = getOracleAssDet(id)
        Oracle_PLevel = ''
        Oracle_Adv_Spec_App = ''
        Oracle_Active_Spec_App = ''
        if CDet:
            if len(str(CDet[0]))>3 and str(CDet[0]) != 'None':
                Oracle_PLevel = "<b>Partnership Level : </b>" + str(CDet[0])  
            if len(str(CDet[2]))>3 and str(CDet[2]) != 'None':
                Oracle_Adv_Spec_App = "<br><b>Advance Specialization Applications : </b>" + str(CDet[2])  
            if len(str(CDet[7]))>3 and str(CDet[7]) != 'None':
                Oracle_Active_Spec_App = "<br><b>Active Specialization Applications : </b>" + str(CDet[7])  
                
        htmlText =  htmlText + Oracle_PLevel + Oracle_Adv_Spec_App + Oracle_Active_Spec_App + str("  </div>")
        


    if data['SAP_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>SAP</h3>  <div>    <p>SAP Partner </p>  </div>")




    if data['VMWare_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>VMWare</h3>  <div>   ")
        CDet = getVMWareAssDet(id)
        VM_PLevel = ''
        VM_Soln_Competency = ''
        VM_PartnerProgram = ''
        VM_VCPs = 0
        VM_VTSPs= 0
        VM_VSPs=0
        VM_VSPCPs = 0 
        VM_VOPs = 0
        VM_ResellerVLEs = 0
        VM_DistiVLEs =0

        #VMPPDet 
# VMWARE Purchasing Program to be added / Partner Program aggregate s
        
        if CDet:
            if len(str(CDet[1]))>3 and str(CDet[1]) != 'None':
                VM_Soln_Competency = "<br><br><b>Solution Competency : </b>" + str(CDet[1])  
            if len(str(CDet[2]))>3 and str(CDet[2]) != 'None':
                VM_PLevel = "<br><br><b>Partnership Level : </b>" + str(CDet[2])  
            if len(str(CDet[3]))>3 and str(CDet[3]) != 'None':
                VM_PartnerProgram = "<br><br><b>Partner Program : </b>" + str(CDet[3])  
            if  CDet[4] > 0 :
                VM_VCPs = str("<br><br><b>VMware Certified Professionals : </b>") + str(CDet[4])
            if  CDet[5] > 0 :
                VM_VTSPs = str("<br><br><b>VMware Technical Solutions Professionals : </b>") + str(CDet[5])
            if  CDet[6] > 0 :
                VM_VSPs = str("<br><br><b>VMware Sales Professionals : </b>") + str(CDet[6])
            if  CDet[7] > 0 :
                VM_VSPCPs = str("<br><br><b>VSPCPs : </b>") + str(CDet[7])
            if  CDet[8] > 0 :
                VM_VOPs = str("<br><br><b>VMware Operations Professionals : </b>") + str(CDet[8])
            if  CDet[9] > 0 :
                VM_ResellerVLEs = str("<br><br><b>Total Reseller VLEs : </b>") + str(CDet[9])
            if  CDet[10] > 0 :
                VM_DistiVLEs = str("<br><br><b>Total Disti VLEs : </b>") + str(CDet[10])
    
        htmlText =  htmlText + VM_PLevel + VM_Soln_Competency + VM_PartnerProgram +VM_VCPs + VM_VTSPs + VM_VSPs + VM_VSPCPs + VM_VOPs +  VM_ResellerVLEs + VM_DistiVLEs +str("  </div>")
    
    
    if data['RH_Partner_ID'].iloc[0] != '' :
        htmlText =  htmlText + str("<h3>RH</h3>  <div>    <p>RH Partner </p>  </div>")
    return htmlText






def getDellAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Dell_Partner_Id  from rhpartners.ptt where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    Dell_Id = ''
    while row is not None:
        Dell_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT `dell_partnerdetails`.`PartnerId`,`dell_partnerdetails`.`Competencies`,`dell_partnerdetails`.`Relationship`  ,`dell_partnerdetails`.`P_PrimaryCustomer`  FROM `rhpartners`.`dell_partnerdetails` where PartnerId like '" + Dell_Id +"' ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cnx.close()
    return row









def getVMWareAssDet(id):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT VMWare_Partner_Id  from rhpartners.ptt where id =" + id +" ;"
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
    query = "SELECT Oracle_Partner_Id  from rhpartners.ptt where id =" + id +" ;"
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
    query = "SELECT MS_Partner_Id  from rhpartners.ptt where id =" + id +" ;"
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
    query = "SELECT Cisco_Partner_Id  from rhpartners.ptt where id =" + id +" ;"
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
    query = "SELECT Citrix_Partner_Id  from rhpartners.ptt where id =" + id +" ;"
    cur = cnx.cursor()
    cur.execute(query)
    row = cur.fetchone()
    Citrix_Id = ''
    while row is not None:
        Citrix_Id =  row[0]
        row = cur.fetchone()
    cur.close()
    
    query = "SELECT Citrix_Partnership_Level,Citrix_Partner_Type, Citrix_Cert_Count, Citrix_Products_Certified_to_Sell,Citrix_Industries_Served,Citrix_Services_Offered,Citrix_Certifications_Held_by_Staff   from rhpartners.citrixportal_partnerdata2 where Citrix_PID like '" + Citrix_Id +"%' ;"
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
    
    
#    try:
#        dummy = session['req']
#    except:
#        session['req'] = 0
#
#    rule = request.url_rule

    
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
    x= DataFrame(x)  
    variable = []
    variable.append([ 'Country' , 'Partners'  ])
    for j in range(0,len(x.ix[:,:])):
        variable.append([str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  x.ix[j,1] ])      
    BarJson = getBarJson()
    return render_template('resultmap.html',  title='Sign In',   dfmap=variable,query=str(query),form = form,Cisco_dummy = CISCO_Partner_req,CITRIX_dummy = CITRIX_Partner_req,MS_dummy = MS_Partner_req,Dell_dummy = Dell_Partner_req,IBM_dummy = IBM_Partner_req,Oracle_dummy = Oracle_Partner_req,VM_dummy = VM_Partner_req,SAP_dummy = SAP_Partner_req,RH_dummy = RH_Partner_req,BarJson = BarJson)







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
#    
#    try:
#        dummy = session['req']
#    except:
#        session['req'] = 0
#
#    rule = request.url_rule

    
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
    x= DataFrame(x)  
    variable = []
    variable.append([ 'Country' , 'Partners'  ])
    for j in range(0,len(x.ix[:,:])):
        variable.append([str(filter(lambda x: x in string.printable, x.ix[j,0])) ,  x.ix[j,1] ])      
    BarJson = getBarJson()
    return render_template('resultmap.html',  title='Sign In',   dfmap=variable,query=str(query),form = form,Cisco_dummy = CISCO_Partner_req,CITRIX_dummy = CITRIX_Partner_req,MS_dummy = MS_Partner_req,Dell_dummy = Dell_Partner_req,IBM_dummy = IBM_Partner_req,Oracle_dummy = Oracle_Partner_req,VM_dummy = VM_Partner_req,SAP_dummy = SAP_Partner_req,RH_dummy = RH_Partner_req,BarJson = BarJson)




def getBarJson():
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT GeoCountry,Count(*) AS Count  from rhpartners.ptt group by GeoCountry Order by 2 desc LIMIT 5;"
    data = pd.read_sql(query,cnx) 
    cnx.close()
    if data is None:
        return ''
    else:
        d1 = data.to_json()
        d1 = data.to_json(orient='records')
        return d1





@app.route('/graphview', methods=['GET', 'POST'])
def graphview():
    form = SearchForm(csrf_enabled=False)
#    results = graph.cypher.execute(
#        "MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) "
#        "RETURN m.title as movie, collect(a.name) as cast "
#        "LIMIT {limit}", {"limit": 100})
#    nodes = []
#    rels = []
#    i = 0
#    for movie, cast in results:
#        nodes.append({"title": movie, "label": "movie"})
#        target = i
#        i += 1
#        for name in cast:
#            actor = {"title": name, "label": "actor"}
#            try:
#                source = nodes.index(actor)
#            except ValueError:
#                nodes.append(actor)
#                source = i
#                i += 1
#            rels.append({"source": source, "target": target})
    return render_template('result.html', form=form )


 

def saveJson():
    result = graph.cypher.execute("MATCH (n:Competitor) RETURN n LIMIT 25")
    data = []
    for i in result:
        dati = collections.OrderedDict()
        dati["CID"] = i[0]
        data.append(dati)
    return result




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
#    if CISCO_Partner_req == ['1']:
#         if len(query)<5:
#             query = query + ' Cisco_Partner_Flag = 1 and Cisco_Ctry_Partner_Flag = 1' 
#         else:
#             query = str(query) + ' and ' +  ' Cisco_Partner_Flag = 1 and Cisco_Ctry_Partner_Flag = 1' 
    
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
             query = query + ' RH_Partner = 1' 
         else:
             query = str(query) + ' and ' +  ' RH_Partner = 1 ' 
                
                
    if RH_Partner_req == '0':
         if len(query)<5:
             query = query + ' RH_Partner != 1' 
         else:
             query = str(query) + ' and ' +  ' RH_Partner != 1 ' 


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
             query = query + ' Global_Partner != 2 ' 
         else:
             query = str(query) + ' and  Global_Partner != 2 '
        
    return query                  









def index():
    user = {'nickname': 'Miguel'}  # fake user
    posts = [  # fake array of posts
        { 
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template("index.html",
                           title='Home',
                           user=user,
                           posts=posts)
                           
                           

                           
                           

    
engine = create_engine('mysql://rbajaj:nxzd8978@localhost') 
engine.execute('use rhpartners;')					 

global csv


def Main():
    return render_template("practise.html")






@app.route('/csv',methods=['GET'])
def csv():
	global csv
	return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=myplot.csv"})	
                 
                 
                 
                 
def getPartners(queryclause):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT Name,GeoCountry,GeoRegion,Partner_Url,id,Coordinates from rhpartners.ptt "
    
    if len(queryclause)>5:        
        query = query + 'WHERE ' + str(queryclause) + ' Order by Coordinates desc LIMIT 250;'     
    else:
        query = query + ' Order by Coordinates desc LIMIT 250 ;'
    data = pd.read_sql(query,cnx)
    
    if data is None:
        return "Username or Password is wrong"
    return data




def getPartnersLoc(queryclause):
    cnx = mysql.connector.connect(user='rbajaj', password = 'nxzd8978',  host='localhost', database='RHPartners')
    query = "SELECT GeoCountry,Count(*) AS Count from rhpartners.ptt "
    
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
    Month = ''
    if date.today().month == 3 or date.today().month == 6 or date.today().month == 9 or date.today().month == 12:    
        Month = 'M1' 
    elif date.today().month == 4 or date.today().month == 7 or date.today().month == 10 or date.today().month == 1:
        Month = 'M2'         
    elif date.today().month == 5 or date.today().month == 8 or date.today().month == 11 or date.today().month == 2:
        Month = 'M3' 
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