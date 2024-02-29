
import os
import csv
import time
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
#window pop
def sep_window_pop(url_path:str)->webdriver:
    '''
    import time
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException    
    '''
    #english version 
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get(url_path)
    time.sleep(1)
       
    return driver
#get category url
def sep_get_cat_url(driver:webdriver)->list[str]:
    '''
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    #sep_window_pop needed
    '''
    try:
        category_container=WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,'//div[@class="accordion filter-card-container"]')))
    except:
        driver.quit()
        time.sleep(1)
        sep_get_cat_url(driver)
        pass
   
    categories_list= category_container.find_element(By.XPATH,'.//div[@class="filter-card-content"]/ul/li/ul')
    categories= categories_list.find_elements(By.XPATH,'./li')

    #get category url list        
    cat_url_list=[]
    for category in categories:
        
        try:
            sub_category_list= category.find_element(By.XPATH,'./ul')   #might not be able to find . like Toner , and skincare sets
            # print(sub_category_list.text)
            sub_categories = sub_category_list.find_elements(By.XPATH,'.//a')
            for sub_category in sub_categories:
                link = sub_category.get_attribute('href')
                cat_url_list.append(link)
            
        except:
            link = category.find_element(By.XPATH,'./a').get_attribute('href')
            cat_url_list.append(link)
            pass
    driver.quit()
    return  cat_url_list
    
#get product url from category url and write it to csv
def sep_get_product_url(url_path:str):
    '''
    import os
    import csv
    import time
    from datetime import date
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support import expected_conditions as EC
    '''

    driver = sep_window_pop(url_path)

    
    #empty product list checking 
    
    try:
        empty_list= driver.find_elements(By.XPATH,'//div[@class="products-container empty"]')    #empty product list checking 
    except NoSuchElementException:      #get product list when its not empty
        print('product list is not empty ')
        
    except Exception as err:
        print(err)
        

    if len(empty_list)>=1:
        
        print('no products found in page')
        driver.quit()
        return
    else:
        try:
            driver.find_element(By.XPATH,'//option[contains(@value,"120")]').click()
            time.sleep(1)
        except:
            pass
        try:
            product_container= WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,'//div[@class="products-grid-container"]')))
        except:
            print('cannot get product container ')

            driver.quit()
            sep_get_product_url(url_path)
    
        
    #get next page btn 
    def next_page_btn_checker()->bool:
        try:
            driver.find_element(By.XPATH,'//a[@class="pagination-item next-page"]')
        except NoSuchElementException:
            
            return False
        return True 
    
    scrape_product:bool= True
    product_url_list=[]
    while scrape_product:
        #srape product url
        time.sleep(2)
        product_list = product_container.find_elements(By.XPATH,'.//div[@class="products-card-container"]')

        print('len of product_list in this page : ' , len(product_list))
        for product in product_list:
            product_link = product.find_element(By.XPATH,'./div/a').get_attribute('href')
            product_url_list.append(product_link)
    
        scrape_product = next_page_btn_checker()
        if scrape_product == True:
            try:
                next_page_btn = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//a[@class="pagination-item next-page"]')))
                next_page_btn.click()
                time.sleep(3)
            except:
                pass
    print('total length of product url list in this category : ',len(product_url_list))
        
    
   
    #product_url_list   call write_csv here 
    if len(product_url_list)!=0:
        write_product_url(product_url_list,url_path)
    else:
        print('product url list is empty !')
        sep_get_product_url(url_path)
        
    print('-------------------------------------------------------')
    return 



def write_product_url(url_list:list[str],original_category_path:str,dir='./sep_csv_folder/sep_prod_url'):
    '''
    from datetime import date
    import os
    import csv
    '''
    
    #original_category_path split check 

    href= original_category_path.split('categories')[-1]
    href_split = href.split('/')
    if len(href_split)==4:
        category_name=href_split[2]
        sub_category_name=href_split[3]
    elif len(href_split)==3:                #if dont have sub_category   category and sub_category share the same name
        category_name=href_split[2]
        sub_category_name=href_split[2]
    else:
        print('get category and sub_category name err')
    
    
    current_date=date.today()
    if not os.path.exists(dir): 
        os.makedirs(dir)
        print("----------------Directory created successfully!")

    csv_path=os.path.join(dir,f'{current_date}_sep_url_{category_name}_{sub_category_name}.csv')
    #create and write csv
    with open (csv_path,'w',newline='',encoding='UTF-8') as csv_file:    
        writer = csv.writer(csv_file)
        writer.writerow(url_list)
        print('write url to csv file , success ! ')
#read csv by given it a date with strict format for date of data == 'YYYY-MM-DD'  or str(date.today())
def read_sep_url_list(date_of_data):
    '''
    # strict format for date of data == 'YYYY-MM-DD'
    import os
    import csv
    '''
    list_url=[]
    dir='./sep_csv_folder/sep_prod_url'
    DoD= str(date_of_data)
    for file in os.listdir(dir):
            csv_path = os.path.join(dir,file)
            if file.startswith(DoD) and file.endswith('.csv'):
                split_name= file.replace('.csv','').split('_')
                cat_subCat=split_name[3:]
                if len(cat_subCat)==2:
                    with open (csv_path,'r') as csv_file:
                        url_reader= csv.reader(csv_file)
                        for url_list in url_reader:
                            for url in url_list:
                                list_url.append([url , cat_subCat])
                else:
                    return 
    return list_url                   

#give it a list contain (url, [category,sub_category]) 
#url for scrape and cateogry for naming csv
def get_product_detail(path_cat_list:list[list[str,list[str]]]):

    '''
    import time 
    from datetime import date
    from selenium import webdriver 
    from selenium.common.exceptions import NoSuchElementException
    #window pop needed
    '''
    #pop a window with any page to begin
    #to ensure driver in on the run 
    #an ready for the looping to use driver.get below
    home_page='https://www.sephora.hk/'
    driver = sep_window_pop(home_page)
    
    # loop over the path_category_list
    for path_cat in path_cat_list:
        url_path= path_cat[0]
        category_name=path_cat[1][0]
        sub_category_name=path_cat[1][1]
        current_date=date.today()
        #set-item filter 
        def set_item_filter():
            for category in path_cat[1]:     #path_cat[1] = ['cat','sub_cat']
                if 'set'in category:
                    return True
                else:
                    return False 

        set_item = set_item_filter()

        if set_item ==False :
            driver.get(url_path) 
            try:
                size_container = WebDriverWait(driver,4).until(EC.presence_of_element_located((By.XPATH,'//ul[contains(@class,"product-variant-swatches")]')))
            except:
                print('size container does not exists , might be as shades , set or item without sizes')
                pass
            # try:
            #     size_container = driver.find_element(By.XPATH,'//ul[@class="product-variant-swatches for-shades"]')
            # except NoSuchElementException:
            #     print('item has no shades, might be as set ')
            #     pass
            # except :
            #     pass

            try:
                #how many time(size) i need to get 
                sizes = size_container.find_elements(By.XPATH,'./li[contains(@class,"product-variant-swatch")]')  
            except:
                sizes= []
                pass
            time.sleep(0.5)
            if len(sizes)!=0:
                for size in sizes:
                    size.click()
                    time.sleep(1)

                    #scrape info after click in different size
                    
                    #locate product info container 
                    try:
                        product_info_container = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,'//div[@class="product-info"]')))
                    except NoSuchElementException:
                        print('product_info_container cannot find ')

                        pass
                    
                    #i should have info container for now , let's get info 
                    #for getting id from class 
                    class_text= size.get_attribute('class')
                    class_text_list = class_text.split(' ')
                    for words in class_text_list:
                        if 'product-variant-swatch-' in words:
                            pre_id= words.split('product-variant-swatch-')
                            product_id = pre_id[-1]
                        else:
                            product_id = None

                    product_brand = special_char_checker(product_info_container.find_element(By.XPATH,'.//div[@class="product-brand"]').text)
                    product_title = special_char_checker(product_info_container.find_element(By.XPATH,'.//div[@class="product-heading"]/h1').text)
                    try:
                        product_size = size.find_element(By.XPATH,'./img').get_attribute('title')
                    except:
                        product_size = size.text

                    price_container = product_info_container.find_element(By.XPATH,'./div/p[@class="product-price"]')
                    #check how many span in price container . from 1 to 3.
                    #if only 1 . it will be the price. if more than one . the sec one would be RRP
                    #i don't need the rest of them
                    ele_in_price = price_container.find_elements(By.TAG_NAME,'span')
                    if len(ele_in_price)==1:
                        product_price= ele_in_price[0].text
                        product_RRP = None
                    elif len(ele_in_price)>1:
                        product_price= ele_in_price[1].text
                        product_RRP =  ele_in_price[0].text
                    else:
                        print('cannot get price and RRP')
                        pass
                    
                    try:
                        product_rating = product_info_container.find_element(By.XPATH,'.//span[@class="product-rating-text"]').text
                    
                    except:
                        product_rating = None
                    product_category = category_name
                    product_sub_category = sub_category_name
                    product_path = driver.current_url
                    product_img_path=driver.find_element(By.XPATH,'//div[@class="image-container tns-item tns-slide-active"]/img').get_attribute('src')


                    product_date = current_date
                    oos_check= product_info_container.find_elements(By.XPATH,'.//div[contains(@class,"product-call-to-action")]')
                    for oos in oos_check:
                        if 'WAITLIST ME'  in oos.text:
                            product_out_of_stock = True
                        else :
                            product_out_of_stock = False
                    result = (product_id,product_brand,product_title,product_size,product_price,product_RRP,product_rating,product_category,product_sub_category,product_path,product_img_path,product_date,product_out_of_stock)
                    #write it to csv
                    sep_data_csv_convertion(result,category_name,sub_category_name)
                    product_info_container=None
                    # print(result)
            print('-----------------------------------')
    return
    
#sep data writer to csv
def sep_data_csv_convertion(product_tuple:tuple,category_name:str,sub_category_name:str,dir='./sep_csv_folder'):
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
    headers=['id','brand','title','size/variant','price','RRP','rating','category','sub_category','path','img_path','date','out_of_stock']
    #csv_path
    csv_path=os.path.join(dir,f'{current_date}_sep_{category_name}_{sub_category_name}.csv')
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

#sephora_product_scarping
def sephora_product_scraping(url):
    
    driver = sep_window_pop(url)
    category_url_list= sep_get_cat_url(driver)  #result would be a list[url:str]
    for link in category_url_list:              #get all product url from different category url
        sep_get_product_url(link)               #it will writer csv for you 

    time.sleep(1)

   

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
#sephora data cleaning
def sephora_data_clean(dir='./sep_csv_folder'):
    '''
    import os
    import pandas as pd
    from datetime import date
    '''

    master_df=pd.DataFrame()

    #dir ='./sep_csv_folder/'		
    current_date =date.today()	#assume you need that 
    for file in os.listdir(dir):
        if file.startswith(str(current_date)) and file.endswith('.csv'):		#condition to locate csv file
        # if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(dir,file))
            master_df=pd.concat([master_df,df],ignore_index=True)
    
    def price_convert(price_str:str):
        if '$' in price_str:
            new_price_str= price_str.replace('$','')
            if ',' in new_price_str:
                sorted_price= new_price_str.replace(',','')
                return float(sorted_price.strip())
            else :
                return float(new_price_str.strip())
        return float(price_str.strip())

    def rrp_convert(rrp_str:str):
        rrp= rrp_str
        if '$' in rrp:
            rrp= rrp.replace('$','')
        if ',' in rrp:
            rrp = rrp.replace(',','')
        if '"' in rrp:
            rrp= rrp.replace('"','')
        return rrp
    

    master_df.drop_duplicates(subset=['path'],inplace=True)
    master_df.price= master_df.price.apply(price_convert)
    master_df.RRP=master_df[~master_df.RRP.isna()].RRP.apply(rrp_convert)
    master_df.RRP.fillna(value=master_df.price,inplace=True)
    master_df.rating.fillna(value='unknown',inplace=True)
    master_df['date'] = pd.to_datetime(master_df['date'])

    clean_data_path=os.path.join(dir,'clean')
    clean_data_name= f'{current_date}_sep_data_clean.csv'

    if not os.path.exists(clean_data_path):
        os.makedirs(clean_data_path)
        print(f"{clean_data_path} created successfully!")
    master_df.to_csv(os.path.join(clean_data_path,clean_data_name))

    return 

#new data checker for insert into db afterward
#and update old_master_df to with new data
def sep_new_item_checker(dir='./sep_csv_folder/clean') :
    '''
    import os 
    import pandas as pd
    from datetime import date
    '''

    new_df=pd.DataFrame()
    dir =dir 
    #read and make two different dataframe and ready to comparison
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
    new_overAll_df=tem_df.drop_duplicates(subset=['id','brand','title','price','RRP','rating', 'path','img_path'],keep='first',ignore_index=True)
    new_sep_data_df = tem_df.drop_duplicates(subset=['id','brand','title','price','RRP','rating', 'path','img_path'],keep=False,ignore_index=True)
    new_product_df =tem_df.drop_duplicates(subset=['id'],keep=False,ignore_index=True)
    #write and update new over all csv and change the name 
    new_overAll_csv_name=f'{current_date}_sep_master_df.csv'
    new_csv_path=os.path.join(dir,new_overAll_csv_name)
    # new_overAll_df.drop(new_overAll_df[new_overAll_df.title.isna()].index,inplace=True)
    new_overAll_df.to_csv(new_csv_path)

    #new_data is ready to insert db
    
    return [new_product_df,new_sep_data_df]

if __name__ == '__main__':   
    print('running sephora_web_scraping.py')
    # start to scrape
    # scrape url only -> csv in sep_prod_url
    cat_target=['skincare','bath-and-body']
    for i in range(len(cat_target)):
        url= f'https://www.sephora.hk/categories/{cat_target[i]}'
        sephora_product_scraping(url)

    #read url csv and scrape product detail
    #give it a date as arg  --> return date of the date type as list[list[str,list[str]]]
    pathAndCategory = read_sep_url_list(str(date.today())) 

    get_product_detail(pathAndCategory)
    time.sleep(1)
    sephora_data_clean()
    new_sep_data_df_list= sep_new_item_checker()         #new_sep_data_df_list is a list contains two df. new_sep_data_df_list[0] = the new product it shows up the first time in your data
                                                         # and new_sep_data_df_list[1] = new data it doesn't have in your record(master_df.csv)