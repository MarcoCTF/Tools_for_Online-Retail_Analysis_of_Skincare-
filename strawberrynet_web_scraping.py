import csv
import os 
import time
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,TimeoutException 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#for window pop-up
def st_window_pop(url_path:str)->webdriver:

    '''
    import time
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException,TimeoutException
    
    '''
    #make sure its english version 
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    driver = webdriver.Chrome(options=options)
    # maximize_window size to get side_bar from responsive UI
    driver.maximize_window()

    driver.get(url_path)

    time.sleep(2)
    try:
        #close the cookies and privacy policy 
        close_privacy_bu = driver.find_element(By.XPATH,'//*[@id="__next"]/div[3]/div[2]/button[2]')
        close_privacy_bu.click()
        time.sleep(2)
    except NoSuchElementException :
        pass
    return driver

#for category url path get
def st_category_looping(driver:webdriver)->list[str]:
    '''
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException,TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    '''


    category_url=[]
    #get all categories
    try:
        categories= WebDriverWait(driver,30).until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class= "MuiBox-root mulltr-s98few"]') ))
    except (NoSuchElementException, TimeoutException ):
        driver.quit()
        time.sleep(1)
        st_category_looping(driver)
    for index in range(len(categories)):
        try:
            categories[index].click()     # expand category
            
        except:
            driver.quit()
            time.sleep(1)
            st_category_looping(driver)
        time.sleep(2)
        sub_category_list = categories[index].find_elements(By.XPATH,'./div/a')
      
        for sub_category in sub_category_list:
            try:
                sub_category.click()
            except:
                driver.quit()
                time.sleep(1)
                st_category_looping(driver)
            time.sleep(3)
            if driver.current_url  in category_url:
                print('url depulicated')
                st_category_looping(driver)
            else:
                category_url.append(driver.current_url)

        # print('-----------------------')
    driver.quit()
    return category_url

#got url_path from 
def product_scrape(url_path:str):
    '''
    from datetime import date
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    #st_window_pop function needed 
    '''


    #only scrap one category/sub_category a time
    driver = st_window_pop(url_path)
    home_page='https://www.strawberrynet.com/en-HK'


    #when params(page) excess its max it will return to home page
    # break point = home_page
    page_num=1
    while driver.current_url != home_page:
        
        #since english version is set 
        category_name = url_path.split('en-HK')[-1].split('/')[-2]
        sub_category_name= url_path.split('en-HK')[-1].split('/')[-1]
        try:
            #locate product container 
            product_container = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,'//div[contains(@class,"product-grid-block")]')))
            products= WebDriverWait(product_container,30).until(EC.presence_of_all_elements_located((By.XPATH,'./div/div[@class="mulltr-1v4jwua"]')))
        
        except TimeoutException  :
            st_csv_rewriter(category_name,sub_category_name)
            time.sleep(1)
            product_scrape(url_path)
            

        #get all product from product
        time.sleep(1)
        for index in range(len(products)):
            

            product_brand = special_char_checker(products[index].find_element(By.XPATH,'./div[@class="MuiBox-root mulltr-16au9q"]/a/div[@class="mulltr-1c9q7kr"]').text)
            product_title = special_char_checker(products[index].find_element(By.XPATH,'./div[@class="MuiBox-root mulltr-16au9q"]/a/div[@class="mulltr-10ac8xq"]').text)
            product_size = special_char_checker(products[index].find_element(By.XPATH,'./div[@class="MuiBox-root mulltr-16au9q"]/a/div[@class="MuiBox-root mulltr-9c7r58"]').text)
            product_price = products[index].find_element(By.XPATH,'./div[@class="MuiBox-root mulltr-orqf19"]/div[1]').text

            
            try:    #RRP might not be exist 
                product_RRP= products[index].find_element(By.XPATH,'./div[@class="MuiBox-root mulltr-orqf19"]/div[@class="MuiBox-root mulltr-2mrm8c"]').text
            except:
                product_RRP=None
                pass


            try:
                product_rating= products[index].find_element(By.XPATH,'./div[@class="MuiBox-root mulltr-orqf19"]/div[@class="MuiBox-root mulltr-70qvj9"]/span').get_attribute("aria-label")
                
            except:
                product_rating=None
                pass

            product_category =category_name
            product_sub_category =sub_category_name
            product_path =  products[index].find_element(By.XPATH,'./a[@class="mulltr-wc71uv"]').get_attribute("href")
            product_img_path = products[index].find_element(By.XPATH,'./a/img').get_attribute("src")
            product_date= date.today()
    
            result = (product_brand,product_title,product_size,product_price,product_RRP,product_rating,product_category,product_sub_category,product_path,product_img_path,product_date)
            st_data_csv_convertion(result,category_name,sub_category_name)
            print('-------------------------------------------------')
        page_num+=1
        product_container =None
        params=f'?page={page_num}'
        print('try to go :' ,url_path+params)
        driver.get(url_path+params)
        time.sleep(3)
        
    driver.quit()
    return    

#use to write data to csv when scraping 
def st_data_csv_convertion(product_tuple:tuple,category_name:str,sub_category_name:str,dir='./st_csv_folder'):
    '''
    import os 
    import csv
    from datetime import date
    '''
    #lib needs=> os, csv, datetime.date
    
    #dir exists checker
    if not os.path.exists(dir):
        os.makedirs(dir)
        print("Directory created successfully!")
   
    #current_date for csv file naming 
    current_date=date.today()
    #csv headers
    headers=['brand','title','size','price','RRP','rating','category','sub_category','path','img_path','date']
    #csv_path
    csv_path=os.path.join(dir,f'{current_date}_st_{category_name}_{sub_category_name}.csv')
    #create and write csv
    with open (csv_path,'a',newline='',encoding='UTF-8') as csv_file:    
        file_is_empty=os.stat(csv_path).st_size==0   #new csv file checking
        st_csv=csv.writer(csv_file)                  #tuple writer 
        if file_is_empty:                            #only write headers the first time 
            st_csv.writerow(headers)
        if len(product_tuple) ==len(headers):
            st_csv.writerow(product_tuple)                       #write tuple to csv
            print('product info write to csv success')
        else:
            print(f'product info must have the same length of headers : {len(headers)}\n---follow by order {headers}')

#use to rewrite csv when occur error in the middle of progress
def st_csv_rewriter(category_name:str,sub_category_name:str,dir='./st_csv_folder' ):
    '''
    import os
    import csv
    from datetime import date
    '''
    headers=['brand','title','size','price','RRP','rating','category','sub_category','path','img_path','date']
    current_date=date.today()
    csv_path=os.path.join(dir,f'{current_date}_st_{category_name}_{sub_category_name}.csv')
    with open (csv_path,'w',newline='',encoding='UTF-8') as csv_file:
        st_csv=csv.writer(csv_file) 
        st_csv.writerow(headers)
    print(f'csv file : {csv_path} has been rewrite')

#strawberry_product_scraping   
def strawberry_product_scraping(url):
    driver = st_window_pop(url)
    url_list= st_category_looping(driver)

    for index in range(len(url_list)):

        product_scrape(url_list[index])
        print("----------")
    


#others
def special_char_checker(info:str):
    #avoid comma in info to csv
    if ',' in info:
        sorted_info = info.replace(',', '-')
        return sorted_info
    elif '®' in info:
        sorted_info = info.replace('®', '-')
        return sorted_info
    elif '™' in info:
        sorted_info=info.replace('™','')
        return sorted_info
    else :
        return info   

#strawberrynet data cleaning
def st_data_clean (dir='./st_csv_folder'):
    '''
    import os
    import pandas as pd
    from datetime import date
    '''

    master_df=pd.DataFrame()

    #dir ='./st_csv_folder/'		
    current_date =date.today()	#assume you need that 
    for file in os.listdir(dir):
        if file.startswith(str(current_date)) and file.endswith('.csv'):		#condition to locate csv file
        # if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(dir,file))
            master_df=pd.concat([master_df,df],ignore_index=True)
    def st_rrp_convert (rrp_str):
        if 'RRP $' in rrp_str:
            rrp_str = rrp_str.replace('RRP $','')
        if ',' in rrp_str :
            rrp_str = rrp_str.replace(',','')
        return rrp_str
    def st_price_convert(price_str):
        if '$' in price_str:
            price_str = price_str.replace('$','')
        if ' ' in price_str:
            price_str = price_str.replace(' ', '')
        if ',' in price_str:
            price_str = price_str.replace(',','')
        return price_str

    

    
    master_df.brand.fillna(value='Strawberry',inplace=True)
    master_df['size']=master_df['size'].str.replace('Size: ','')
    master_df.rating=master_df.rating.str.replace(' Stars','').str.replace(' Star','')
    master_df.rating.fillna(value='unknown',inplace=True)
    master_df.price=master_df.price.apply(st_price_convert)
    master_df.RRP.fillna(value=master_df.price,inplace=True)
    master_df.RRP=  master_df[~master_df.RRP.isna()].RRP.apply(st_rrp_convert)
    master_df.RRP=master_df.RRP.astype(float)
    master_df.price=master_df.price.astype(float)
    master_df['date']=pd.to_datetime(master_df['date'])

    clean_data_path=os.path.join(dir,'clean')
    clean_data_name= f'{current_date}_st_data_clean.csv'

    if not os.path.exists(clean_data_path):
        os.makedirs(clean_data_path)
        print(f"{clean_data_path} created successfully!")
   

    master_df.to_csv(os.path.join(clean_data_path,clean_data_name))

    result = extract_ids_from_urls(master_df,'path')
    return  result

def extract_ids_from_urls(dataframe, column_name):
    url_list = list(dataframe[column_name])
    id_list = []

    for url in url_list:
        id_list.append(url.split('/')[-1])

    return id_list

#new data checker for insert into db afterward
#and update old_master_df to with new data
def st_new_item_checker(dir='./st_csv_folder/clean') :
    '''
    import os 
    import pandas as pd
    from datetime import date
    '''
    # hard_code_dir = ./st_csv_folder/clean

    new_df=pd.DataFrame()
    dir =dir 
    #reead and make two different dataframe and ready to comparison
    for file in os.listdir(dir):
        if file.endswith('master_df.csv'):
            overAll_df= pd.read_csv(os.path.join(dir,file))
        else : 
            overAll_df=pd.DataFrame()

        if file.endswith('clean.csv'):
            df = pd.read_csv(os.path.join(dir,file))
            new_df=pd.concat([new_df,df],ignore_index=True)
            

    current_date = date.today()
    

    #overAll_df as old data
    #df as new cleaned data
    tem_df= pd.concat([overAll_df,new_df],ignore_index=True)

    #might need to thing about what to keep or not 
    new_overAll_df=tem_df.drop_duplicates(subset=['product_id','brand','title','price','RRP','rating', 'path','img_path'],keep='first',ignore_index=True)
    new_st_data_df = tem_df.drop_duplicates(subset=['product_id','brand','title','price','RRP','rating', 'path','img_path'],keep=False,ignore_index=True)
    new_product_df = tem_df.drop_duplicates(subset=['product_id'],keep=False,ignore_index=True)
    #write and update new over all csv and change the name 
    new_overAll_csv_name=f'{current_date}_st_master_df.csv'
    new_csv_path=os.path.join(dir,new_overAll_csv_name)
    new_overAll_df.to_csv(new_csv_path)

    #new_data is ready to insert to db
    
    return [new_product_df, new_st_data_df]
    




if __name__ == '__main__':
    print('running strawberrynet_web_scraping.py')
    
    # start to scrape
    url='https://www.strawberrynet.com/en-HK/skincare'
    url_list = strawberry_product_scraping(url)

    
    st_data_clean()                                # it could do just data cleaning 
    # product_id_list = st_data_clean()            # it also comes with a return as the product_id_list if you need that
    
    
    new_st_data_df_list =st_new_item_checker()          #new_st_data_df_list is a list contains two df. new_st_data_df_list[0] = the new product it shows up the first time in your data
                                                        # and new_st_data_df_list[1] = new data it doesn't have in your record(master_df.csv)