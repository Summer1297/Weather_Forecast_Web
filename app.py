from cmath import e
from bs4 import BeautifulSoup
from flask import Flask, request, url_for, redirect, render_template
import requests
from geopy.geocoders import Nominatim   # Get latitude and longitude by city name
import json

app = Flask(__name__)

@app.route("/")  # The initial search page doesn't need input any parameter.
def index():
    return render_template('index.html')  # The initial search page.


@app.route("/<city>")  # input 'city' 
def city_weather(city):
    weather_data = find_weather(city) # call the method to get weather data as result.
    return render_template("city_weather_google.html", weather_data = weather_data)  # and skip to the search result page.

    #weather_data = getLatLong(city) 
    #return render_template("city_weather_api.html", weather_data = weather_data)  

def getLatLong(city):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    } 
    geolocator = Nominatim(user_agent="txia5002_final")
    location = geolocator.geocode(city)
    lat_lon_str = str(location.latitude) + "," + str(location.longitude)
    
    res = requests.get(
            f'https://api.weather.gov/points/{lat_lon_str}', headers=headers)
    city_detail = res.json()
    
    wea_detail_url = city_detail['properties']['forecast']
    
    city_loc_info =city_detail['properties']['relativeLocation']['properties']['city'] + ','+ city_detail['properties']['relativeLocation']['properties']['state']
    print(city_loc_info)
    wea_detail_res= requests.get(wea_detail_url,headers=headers)
    
    wea_detail_json = wea_detail_res.json()
    
    #print(wea_detail_json['properties']['periods'][0])
    
    wea_14 = wea_detail_json['properties']['periods']
    
    return wea_14 
    
        
def find_weather(city_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }  # identify the application, operating system, vendor, and/or version of the requesting user agent.
    
    city_name = city_name.replace(" ", "+")
    try:
        res = requests.get(
            f'https://www.google.com/search?q={city_name}+weather', headers=headers)  # requests to get data 
        
        soup = BeautifulSoup(res.text, 'html.parser')    # The BeautifulSoup packages contain statement to get html data.
        print(soup)
        location = soup.select('#wob_loc')[0].getText().strip()    # There tag such as "wob_loc" are come from the webstie
        time = soup.select('#wob_dts')[0].getText().strip()        # .strip() is used to remove beginning and end spaces of the string.
        info = soup.select('#wob_dc')[0].getText().strip()         
        temperature = soup.select('#wob_tm')[0].getText().strip() 
        precipitation = soup.select('#wob_pp')[0].getText().strip()
        humidity = soup.select('#wob_hm')[0].getText().strip()
        wind = soup.select('#wob_ws')[0].getText().strip()
        week_weather = soup.select('#wob_dp')[0]                   # all of this can get the weather info
        
        print("Location: " + location 
              + "\nTemperature: " + temperature + "°F" 
              + "\nTime: " + time  
              + "\nWeather Description: " + info
              + "\nPrecipitation: " + precipitation
              + "\nHumidity: " + humidity
              + "\nWind: " + wind
              + "\n- - - - - - - - - - - - - - - - - - - -\n")
        
        ## Save the resulting data as a dictionary. in order to put in my html conveniently.
        today_wea = {'location': location,
                    'temperature': temperature, 'time':time, 'info':info, 'precipitation':precipitation, 'humidity': humidity, 'wind':wind
                   }
        
        first_day = 0 # As a index to find the day in for loop, it will be used to a key in dictionary.
        
        for x in week_weather:  
            weather_of_week = []
            day_of_week = x.next_element.getText()  
            print('Day of week: '+ day_of_week)  
            first_day += 1  
            weather_of_week.append(day_of_week)  # add the data into a list.
              
            for temp in x.find_next('span', style=True):
                
                
                max_temp_f = temp.get_text()
                min_temp_f = temp.find_next().find_next().find_next().getText()
                #max_temp_c = temp.find_next().getText()            # Maximum temperature of Centigrade
                #min_temp_c = temp.find_next().find_next().find_next().find_next().getText()   # Minimum temperature of Centigrade
                
                weather_of_week.append(max_temp_f)
                weather_of_week.append(min_temp_f)  # add the data into a list.
                #weather_of_week.append(max_temp_c)
                #weather_of_week.append(min_temp_c)
                      
                print('Max temp: ' + max_temp_f + '°F')  # Maximum temperature of Fahrenheit
                print('Lowest temp: '+ min_temp_f + '°F')  # Minimum temperature of Fahrenheit
                #print('Max temp: ' + max_temp_c + '°C')  
                #print('Lowest temp: '+ min_temp_c + '°C')  

            for desc in x.find_all_next('img', alt=True):  ## thorough the img tag to find 'alt' to search i need
                weather_info = desc['alt']
                weather_of_week.append(weather_info)
                print("Weather Description: " + weather_info)
                today_wea[first_day] = weather_of_week  # first_day as a key and weather_of_week as value ,store them into dictionary
               
                break
                
        return today_wea
    
  
    except:
        pass
