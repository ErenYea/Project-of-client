from types import ClassMethodDescriptorType
from main.scrape import Scrape
import csv


inst = Scrape()
inst.land_on_first_page()
try:
    inst.click_on_popup()
except:
    print("cannotfind")
inst.select_contry()
print('*******************************************************************')
print('********************** Printing States ****************************')
print('\n')
inst.get_states()
print('\n')
print('********************************************************************')
print('\n')
state = input("Enter the value of state from above list or Just press Enter to Directly Use TEXAS : ")
inst.input_state(state=state)
print('\n')
choice = input("Type 'Y' to chose by state or Type 'N' for chose by city: ").lower()
if choice == 'n':
    with open('cities.csv','r',encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            for  i in row:
                inst.cities.append(i)
                print(i,end=' , ')
    inst.select_date()
    print('\n')
    date_from = input("Enter the date from in format mm/dd/yyyy: ")
    print('\n')
    date_to = input("Enter the date to in format mm/dd/yyyy: ")
    inst.date_range(date_from=date_from,date_to=date_to)
    for i in inst.cities:
        keyword = i
        inst.keyword(keyword=keyword)
        inst.search()
        result_cond = inst.get_result()
        if result_cond == 'Didnot':
            continue
        inst.click_all_results()
        inst.scrolldown()
        inst.result_to_csv()
        inst.runscrapper()

else:
    inst.select_date()
    while True:
        print('\n')
        date_from = input("Enter the date from in format mm/dd/yyyy: ")
        print('\n')
        date_to = input("Enter the date to in format mm/dd/yyyy: ")
        inst.date_range(date_from=date_from,date_to=date_to)
        inst.search()
        result_cond = inst.get_result()
        print(result_cond)
        if result_cond == False:
            break
        elif result_cond == 'Didnot':
            print('\n************************************************')
            print('***************** No result ********************')
            print('\n')
            print('Quitiing')
            quit()
        print("Result Exceeded from limit \nplease reduced the date range")
    inst.click_all_results()
    inst.scrolldown()
    inst.result_to_csv()
    inst.runscrapper()
print("Result got")
inst.df.to_excel(r'result.xlsx', index = False)