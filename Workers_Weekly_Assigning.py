#!/usr/bin/env python
# coding: utf-8

# In[27]:


# Clean all variables, import libraries, print the script cause
for name in dir():
    if not name.startswith('_'):
        del globals()[name]

import pandas as pd
import numpy as np

print ('This script returns the next weeks assigning')  


# In[28]:


## Download all gsheets as csvs

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('Assigning-5e936764c747.json', scope)

gc = gspread.authorize(credentials)

def download_file(url, filename):
    ''' Downloads file from the url and save it as filename '''
    # check if file already exists
    if not os.path.isfile(filename):
        print('Downloading File')
        response = requests.get(url)
        # Check if the response is ok (200)
        if response.status_code == 200:
            # Open file and write the content
            with open(filename, 'wb') as file:
                # A chunk of 128 bytes
                for chunk in response:
                    file.write(chunk)
    else:
        print('File exists')


# Get the names of the workers from the file list_of_workers.txt
import io
with io.open("list_of_workers.txt", 'r', encoding='utf8') as f:
    Workers = f.read().split(',')
    Workers_names = Workers.copy()
    
str = "%s"%Workers_names[0]
Workers_names[0]=str.replace("\ufeff", "")
Workers_number=len(Workers)


# Download the assigning requests of each workers as csv
for i in range(0,Workers_number):
        print(Workers[i])
        Workers[i] = gc.open("%s"% Workers_names[i])
        url = 'https://docs.google.com/spreadsheet/ccc?key=%s&output=csv' % Workers[i].id
        filename = '%s.csv' % Workers[i].title
        download_file(url, filename)

                
print('Finished downloading all files!')


# In[29]:


# Python is having trouble reading a csv file with a hebrew title, so change it to ordinal numbers
for i in range(0,Workers_number):
    os.rename('%s.csv' % Workers_names[i], '%s.csv'%i)

## Create the Workers' requests Matrix:

for i in range(0,Workers_number):
        Workers[i]=pd.read_csv('%s.csv'%i) 
        Workers[i]=Workers[i].loc["0":"13","ראשון":"חמישי"]
        Workers[i]=Workers[i].values
        Workers[i]=Workers[i].astype(int)
        print(Workers_names[i])
        print(Workers[i])
        os.remove('%s.csv'%i)


# In[30]:


# We now have all the workers requests in "Workers"!
##  Create the final assignemnt Matrix - 0 for unassigned hour, 1 for assigned hour.
#  The number of workers for each day is as follows:
# 1 worker until 10:00 (blocks 0,1)
# 2 workers until 14:00 (blocks 2-5)
# 3 workers until 18:00 (blocks 6-9)
# 2 workers until 19:00 (block 10)
# 1 workers until 22:00 (block 11-13)

sunday=np.array([[0]*2,[0]*2, [0,0]*2,[0,0]*2,[0,0]*2,[0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0]*2,[0]*2,[0]*2,[0]*2])
monday=np.array([[0]*2,[0]*2, [0,0]*2,[0,0]*2,[0,0]*2,[0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0]*2,[0]*2,[0]*2,[0]*2])
tuesday=np.array([[0]*2,[0]*2, [0,0]*2,[0,0]*2,[0,0]*2,[0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0]*2,[0]*2,[0]*2,[0]*2])
wednesday=np.array([[0]*2,[0]*2, [0,0]*2,[0,0]*2,[0,0]*2,[0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0]*2,[0]*2,[0]*2,[0]*2])
thursday=np.array([[0]*2,[0]*2, [0,0]*2,[0,0]*2,[0,0]*2,[0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0,0]*2,[0,0]*2,[0]*2,[0]*2,[0]*2])

# The entire assigning is 5 days:
assignings=(sunday,monday,tuesday,wednesday,thursday)

# Create a dataframe:
df = pd.DataFrame({i+1:x for i,x in enumerate(assignings)})
df= df.rename(index={0:'7:30-9:00',1:'9:00-10:00',2:'10:00-11:00',3:'11:00-12:00',4:'12:00-13:00',5:'13:00-14:00',6:'14:00-15:00',7:'15:00-16:00',8:'16:00-17:00',9:'17:00-18:00',10:'18:00-19:00',11:'19:00-20:00',12:'20:00-21:00',13:'21:00-22:00'})
df = df.rename(columns={1:'ראשון',2:'שני',3:'שלישי',4:'רביעי',5:'חמישי'})

# Calc the total number of hours:
max_hours_for_worker=0
count=0
for key, value in df.iteritems(): 
    for index, row in df.iterrows():
        max_hours_for_worker+=len(df.loc[index,key])
max_hours_for_worker=int(max_hours_for_worker/2)
df 


# In[31]:


# Create the draft of picking: there are total_hours_number for each the worker, so run max_hours_for_worker*Workers_number times:
Running_times=max_hours_for_worker*Workers_number
draft=np.empty(0, dtype=int)

for d in range(0,Running_times):
    a=np.random.choice(Workers_number,Workers_number,replace=False)
    draft=np.append(draft,a)
print(draft[0:200])
print(len(draft))


# In[32]:


### THE ASSIGNINGS!

finished_workers=np.zeros(Workers_number,dtype=int)
eight_hours_for_worker = pd.DataFrame(index=['ראשון','שני','שלישי','רביעי','חמישי'],columns=Workers_names)
counter=0
hours_this_day=0
hours_got_this_draft=0
# Run the draft:
for chosen_worker in draft: 
    counter+=1
    print('The chosen worker is %s ############'% Workers_names[chosen_worker])
    worker_request = pd.DataFrame(Workers[chosen_worker])
    worker_request = worker_request.rename(index={0:'7:30-9:00',1:'9:00-10:00',2:'10:00-11:00',3:'11:00-12:00',4:'12:00-13:00',5:'13:00-14:00',6:'14:00-15:00',7:'15:00-16:00',8:'16:00-17:00',9:'17:00-18:00',10:'18:00-19:00',11:'19:00-20:00',12:'20:00-21:00',13:'21:00-22:00'})
    worker_request = worker_request.rename(columns={0:'ראשון',1:'שני',2:'שלישי',3:'רביעי',4:'חמישי'})
    # Skip the worker if all of his hours were already checked:
    if len(worker_request[(worker_request>0)&(worker_request<11)].min().dropna().value_counts()) == 0:
        print("<--All of this worker's hours we're assigned or unavailable, skipping to next worker")
        finished_workers[chosen_worker]=chosen_worker+1
        # If finished going through all the workers' choices, stop the draft:
        if len(finished_workers.nonzero()[0])==Workers_number:
            break 
    else:
        print(worker_request)
        # While the worker didn't get any hour and we didn't go throught all of the worker's hours, go through all of his preferences levels:
        while hours_got_this_draft==0 and len(worker_request[(worker_request>0)&(worker_request<11)].min().dropna().value_counts()) > 0:
            # Find best preffered hours in all days:(must be bigger than 0 and less or equal to 10)
            best_hours_all_days=worker_request[(worker_request>0)&(worker_request<11)].min().dropna().index
            days_long_format=eight_hours_for_worker.loc[best_hours_all_days,Workers_names[chosen_worker]].isna().where(eight_hours_for_worker.loc[best_hours_all_days,Workers_names[chosen_worker]].isna() == True).dropna().index.values
            days_available={}
            # If not all of the days contain 8 hours already, get a random minial day which doesn't have 8 hours already:
            if len(days_long_format)>0:
                for i in range(0,len(days_long_format)):
                    days_available[i]=days_long_format[i]
                worker_request_not_eight_hours = pd.DataFrame(worker_request.loc[:,days_available.values()])
                origional_preference_level=int(worker_request_not_eight_hours[(worker_request_not_eight_hours>0)&(worker_request_not_eight_hours<11)].min().dropna().min())
                preffered_days=worker_request_not_eight_hours[(worker_request_not_eight_hours>0)&(worker_request_not_eight_hours<11)].min().dropna()==origional_preference_level
                preffered_days=preffered_days.where(preffered_days == True).dropna()
                preffered_day=preffered_days.sample().index[0]
                preffered_day_position=worker_request.columns.get_loc(preffered_day)
            # If all of the days contain 8 hours already, just pick the minimal random one:
            else:
                # Find the most preffered hour: (must be bigger than 0 and less or equal to 10)
                print('בכל הימים הפנויים של העובד כבר היו 8 שעות, בחרנו בלית ברירה יום רנדומלי') 
                origional_preference_level=int(worker_request[(worker_request>0)&(worker_request<11)].min().dropna().min())
                preffered_days=worker_request[(worker_request>0)&(worker_request<11)].min().dropna()==origional_preference_level
                preffered_days=preffered_days.where(preffered_days == True).dropna()
                preffered_day=preffered_days.sample().index[0]
                preffered_day_position=worker_request.columns.get_loc(preffered_day)    
            # In the assigned day, find the best hour:
            preffered_hour=worker_request.loc[(worker_request.loc[:,preffered_day]>0)&(worker_request.loc[:,preffered_day]<11),preffered_day].idxmin()
            preffered_hour_position=worker_request.index.get_loc(preffered_hour)
            print('העובד רוצה את שעה %s ביום %s' %(preffered_hour,preffered_day))
            print('This hour is assigned to:')
            print(df.loc[preffered_hour,preffered_day])
            worker_name=Workers_names[chosen_worker]
            # Check the number of hours the worker already got on this day, add it to hours_this_day, only if there are no 8 hours already, since in this case it's OK to have more
            if worker_request.loc[worker_request.loc[:,preffered_day].gt(10),preffered_day].count()<8:
                hours_this_day=worker_request.loc[worker_request.loc[:,preffered_day].gt(10),preffered_day].count()
            ## Check the next hour's preference level:
            # only if we're not in the last hour
            if preffered_hour_position<14:
                if preffered_hour_position<13:
                    next_preference_level=int(worker_request.iloc[preffered_hour_position+1,preffered_day_position])
                # If it's a block of several hours:
                if (next_preference_level == origional_preference_level):
                    # While in the same day and same preference level, check if the hour is available:
                    while ((preffered_hour_position<14) and (next_preference_level == origional_preference_level) and (hours_this_day<8)):
                        # if the hour is available, get it, else, check the next hour:
                        if 0 in df.iloc[preffered_hour_position,preffered_day_position] :
                            if hours_this_day<=7:
                                print("The hour is available, giving it to %s" % worker_name )
                                available_place=df.iloc[preffered_hour_position,preffered_day_position].index(0)
                                df.iloc[preffered_hour_position,preffered_day_position][available_place]=worker_name
                                hours_got_this_draft+=1
                                print("Hours got this draft: %s"%hours_got_this_draft)
                                print('The worker got the hour, add 10 to it')
                                worker_request.iloc[preffered_hour_position,preffered_day_position]=worker_request.iloc[preffered_hour_position,preffered_day_position]+10
                                Workers[chosen_worker]
                                worker_request
                                print('Number hours for the worker today:')
                                hours_this_day+=1
                                print (hours_this_day)
                                if hours_this_day==8:
                                    eight_hours_for_worker.loc[preffered_day,Workers_names[chosen_worker]]=1
                                # next hour, only if it's not the last hour:
                                preffered_hour_position+=1
                                if preffered_hour_position<13:
                                    print('After assigning hour, check next hour')
                                    next_preference_level = int(worker_request.iloc[preffered_hour_position,preffered_day_position]) 
                            else:
                                print('The Worker got 8 hours already, not giving it to the worker')
                        else:
                            print('The worker didnt got the hour, change it to minus the preference level:')
                            worker_request.iloc[preffered_hour_position,preffered_day_position]= worker_request.iloc[preffered_hour_position,preffered_day_position]*-1
                            # next hour, only if it's not the last hour:
                            preffered_hour_position+=1
                            if preffered_hour_position<13:
                                print('After NOT assigning hour, check next hour')
                                next_preference_level = int(worker_request.iloc[preffered_hour_position,preffered_day_position]) 
                # If it's only one hour:
                else:
                    if 0 in df.iloc[preffered_hour_position,preffered_day_position] :
                        print("The hour is available, giving it to %s" % worker_name )
                        hours_this_day+=1
                        hours_got_this_draft+=1
                        print("Hours got this draft: %s"%hours_got_this_draft)
                        available_place=df.iloc[preffered_hour_position,preffered_day_position].index(0)
                        df.iloc[preffered_hour_position,preffered_day_position][available_place]=worker_name
                        print('The worker got the hour, add 10 to it')
                        worker_request.iloc[preffered_hour_position,preffered_day_position]=worker_request.iloc[preffered_hour_position,preffered_day_position]+10
                        Workers[chosen_worker]
                        worker_request
                    else:
                        print('The worker didnt got the hour, change it to minus the preference level:')
                        worker_request.iloc[preffered_hour_position,preffered_day_position]= worker_request.iloc[preffered_hour_position,preffered_day_position]*-1
            Workers[chosen_worker]=pd.DataFrame(worker_request)
            print(Workers[chosen_worker])
            print('Finished searching more avilable hour in the day, picking the next worker')    
            hours_this_day=0
        hours_got_this_draft=0
print('!The draft is... done')   
print("The maximum possible blocks of hours requests is %s, but the workers' requests were only %s"%(len(draft),counter))


# In[33]:



# Report the unassigned hours that no one requested
missing_hours = pd.DataFrame()
missing_hours["יום"] = ""
missing_hours["שעה"] = ""
missing_hours["מספר עובדים חסרים"] = ""
days={}
hours={}
worker_num={}
p=1

counter=0
for key, value in df.iteritems(): 
    for index, row in df.iterrows():
        for i in range(0,len(df.loc[index,key])):
            if 0 in df.loc[index,key]:
                #print (key,index,i)
                hours[counter]=index
                days[counter]=key
                counter+=1
                break
                '''if 
                missing_hours.loc[p,"שעות חסרות"]=key,index
                missing_hours.loc[p,"מספר עובדים חסרים"]=i
                p+=1'''
for i in range(0,len(days)):
    worker_num[i]=df.loc[hours[i],days[i]].count(0)

for i in range(0,len(days)):
    missing_hours.loc[p,'יום']=days[i]
    missing_hours.loc[p,'שעה']=hours[i]
    missing_hours.loc[p,'מספר עובדים חסרים']=worker_num[i]
    p+=1


import datetime

t=datetime.datetime.now()
date="%s_%s_%s"%(t.day,t.month,t.year)

#missing_hours.to_excel("Unassigned_hours_%s.xlsx"%date)
missing_hours


# In[34]:


## Divide into social - ח and central, save as file

#social=df.copy(deep=True)
#central=df.copy(deep=True)

for key, value in df.iteritems(): 
    for index, row in df.iterrows():
        #social.loc[index,key]=[]
        #central.loc[index,key]=[]
        for i in range(0,len(df.loc[index,key])):
            if (i+1) % 2 == 0:
                #social.loc[index,key].append(df.loc[index,key][i])
                df.loc[index,key][i]="%s - ח"%df.loc[index,key][i]
            #else:
                #central.loc[index,key].append(df.loc[index,key][i])

#df.to_excel("Shibutzim_%s.xlsx"%date)

df


# In[35]:


## Create the justice table:
justice_table = pd.DataFrame(index=['אחוז השעות שקיבלו','סך השעות שקיבלו','סך השעות ששיבצו','רמה 1','רמה 2','רמה 3','רמה 4','רמה 5','רמה 6','רמה 7','רמה 8','רמה 9','רמה 10'],columns=Workers_names)
sum_hours_all_workers=0
total_percentage_all_workers=0
less_than_zero_all_workers=0
level_all_workers=np.zeros(10,dtype=int)
number_of_workers_in_each_level=np.zeros(10,dtype=int)
sum_level_all_workers=np.zeros(10,dtype=int)
sum_requested_level_all_workers=np.zeros(10,dtype=int)
import warnings
warnings.filterwarnings("ignore")
for i in range(0,Workers_number):
    current_worker = pd.DataFrame(Workers[i])
    sum_hours=current_worker.select_dtypes(include='int').gt(0).sum().sum()
    sum_hours_all_workers+=sum_hours
    justice_table.iloc[1,i]=sum_hours
    less_than_zero=current_worker.select_dtypes(include='int').lt(0).sum().sum()
    less_than_zero_all_workers+=less_than_zero
    total_percentage=round(sum_hours/(sum_hours+less_than_zero)*100,2)
    total_percentage_all_workers+=total_percentage
    percentage_string="%s%%"%total_percentage
    justice_table.iloc[0,i]=percentage_string
    justice_table.iloc[2,i]=sum_hours+less_than_zero
    level_counter=3
    for j in range(1,11):
        level=round(current_worker.select_dtypes(include='int').eq(j+10).sum().sum()/(current_worker.select_dtypes(include='int').eq(j+10).sum().sum()+current_worker.select_dtypes(include='int').eq(j*-1).sum().sum())*100,2)
        if np.isnan(level):
            justice_table.iloc[level_counter,i]=""
        else:
            level_string="%s%%"%level
            sum_level_all_workers[level_counter-3]+=level
            number_of_workers_in_each_level[level_counter-3]+=1
            justice_table.iloc[level_counter,i]=level_string
            level_counter+=1
justice_table['העובד הממוצע']=""
total_percentage_all_workers=int(round(sum_hours_all_workers/(sum_hours_all_workers+less_than_zero_all_workers)*100))
percentage_string_all_workers="%s%%"%total_percentage_all_workers
justice_table.loc['אחוז השעות שקיבלו','העובד הממוצע']=percentage_string_all_workers
justice_table.loc['סך השעות שקיבלו','העובד הממוצע']=int(round(sum_hours_all_workers/Workers_number))
justice_table.loc['סך השעות ששיבצו','העובד הממוצע']=int(round((sum_hours_all_workers+less_than_zero_all_workers)/Workers_number))
avg_level_all_workers=np.zeros(10,dtype=int)

for k in range(0,10):
    if number_of_workers_in_each_level[k]==0:
        avg_level_all_workers[k]=-1
    else:
        avg_level_all_workers[k]=(sum_level_all_workers[k]/(number_of_workers_in_each_level[k]*100))*100
        justice_table.iloc[k+3,Workers_number]="%s%%"%avg_level_all_workers[k]

justice_table=justice_table.fillna("")
justice_table=justice_table.replace(to_replace=-1, value="")

#justice_table.to_excel("Justice_table_%s.xlsx"%date)
justice_table


# In[36]:


with pd.ExcelWriter('Assignings_%s.xlsx'%date) as writer:  
    df.to_excel(writer, sheet_name='שיבוצים')
    missing_hours.to_excel(writer, sheet_name='שעות פנויות')
    justice_table.to_excel(writer, sheet_name='טבלת צדק')


# In[37]:


print ('The script is DONE!')  


# In[ ]:




