import scrapy
import pandas as pd
import time

link = "https://www.houzz.com/professionals/general-contractor/san-jose-ca-us-probr0-bo~t_11786~r_5392171?fi=4965"
first_page = 'https://www.houzz.com/professionals/general-contractor/san-jose-ca-us-probr0-bo~t_11786~r_5392171?fi=0'
details = {
        
'BusinessName':"",
'Emailaddress':"",
'NumberofReviews':"",
'ReviewRating':"",
'Phonenumber':"",
'Licensenumber':"",
'Website':"",
'Address':"",
'businessownerName':"",
'socialmediaLinks':"",
}
