#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
利用splinter写的一个手动过验证及自动抢票的例子，
大家可以自己扩展或者弄错窗体、web端。
本例子只做参考。
本代码发布于2018.12.18（如果报错请查看官网是否改动）
'''
import re
from splinter.browser import Browser
from time import sleep
import sys
import httplib2
from urllib import parse
import smtplib
from email.mime.text import MIMEText


class BrushTicket(object):
    """买票类及实现方法"""

    def __init__(self,train_date, user_name, password, passengers, from_time, from_station, to_station,  seat_type, receiver_mobile, receiver_email,isHave=False,):
        """定义实例属性，初始化"""
        # 有票就行
        self.isHave = isHave
        # 1206账号密码
        self.user_name = user_name
        self.password = password
        # 乘客姓名
        self.passengers = passengers
        # 起始站和终点站
        self.from_station = from_station
        self.to_station = to_station
        # 乘车日期
        self.from_time = from_time
        #发车时间
        self.train_date=train_date
        # 座位类型所在td位置
        if seat_type == '商务座特等座':
            seat_type_index = 1
            seat_type_value = 9
        elif seat_type == '一等座':
            seat_type_index = 2
            seat_type_value = 'M'
        elif seat_type == '二等座':
            seat_type_index = 3
            seat_type_value = 0
        elif seat_type == '高级软卧':
            seat_type_index = 4
            seat_type_value = 6
        elif seat_type == '软卧':
            seat_type_index = 5
            seat_type_value = 4
        elif seat_type == '动卧':
            seat_type_index = 6
            seat_type_value = 'F'
        elif seat_type == '硬卧':
            seat_type_index = 7
            seat_type_value = 3
        elif seat_type == '软座':
            seat_type_index = 8
            seat_type_value = 2
        elif seat_type == '硬座':
            seat_type_index = 9
            seat_type_value = 1
        elif seat_type == '无座':
            seat_type_index = 10
            seat_type_value = 1
        elif seat_type == '其他':
            seat_type_index = 11
            seat_type_value = 1
        else:
            seat_type_index = 7
            seat_type_value = 3
        self.seat_type_index = seat_type_index
        self.seat_type_value = seat_type_value
        # 通知信息
        self.receiver_mobile = receiver_mobile
        self.receiver_email = receiver_email
        # 主要页面网址
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'
        self.init_my_url = 'https://kyfw.12306.cn/otn/view/index.html'
        self.ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init'
        # 浏览器驱动信息，驱动下载页：https://sites.google.com/a/chromium.org/chromedriver/downloads
        self.driver_name = 'chrome'
        #驱动的位置
        self.executable_path = 'D:/chromedriver.exe'

    def do_login(self):
        """登录功能实现，手动识别验证码进行登录"""
        self.driver.visit(self.login_url)
        sleep(1)
        self.driver.fill('loginUserDTO.user_name', self.user_name)
        self.driver.fill('userDTO.password', self.password)
        print('请输入验证码……')
        while True:
            if self.driver.url != self.init_my_url:
                sleep(1)
            else:
                break

    def start_brush(self):
        """买票功能实现"""
        self.driver = Browser(driver_name=self.driver_name,executable_path=self.executable_path)
        # 浏览器窗口的大小
        # self.driver.driver.set_window_size(900, 700)
        self.do_login()
        self.driver.visit(self.ticket_url)
        try:
            print('开始刷票……')
            # 加载车票查询信息
            self.driver.cookies.add({"_jc_save_fromStation": self.from_station})#出发位置
            self.driver.cookies.add({"_jc_save_toStation": self.to_station})#目的地
            self.driver.cookies.add({"_jc_save_fromDate": self.from_time})#出发时间
            self.driver.reload()
            count = 113230
            while self.driver.url.split('?')[0] == self.ticket_url:
                try:
                    self.wait_time('query_ticket')
                    elemt= self.driver.find_by_xpath('//select[@id="cc_start_time"]//option[@value="'+str(self.train_date)+'"]',).first
                    elemt.click()
                    sleep(1)
                    self.driver.find_by_text('查询').click()
                    self.wait_time('train_type_btn_all')
                    count += 1
                    print('第%d次点击查询……' % count)
                    
                    elems = self.driver.find_by_id('queryLeftTable')[0].find_by_xpath('//tr[starts-with(@id,"ticket_")]')
                    while len(elems)==0:
                        sleep(0.5)
                        elems = self.driver.find_by_id('queryLeftTable')[0].find_by_xpath('//tr[starts-with(@id,"ticket_")]')
                    #是不是有票就行
                    if(self.isHave):
                        for current_tr in elems:
                            if(current_tr.text==''):
                                print('没票')
                                continue
                                # 下标索引
                            if current_tr.find_by_tag('td')[self.seat_type_index].text == '--' or current_tr.find_by_tag('td')[self.seat_type_index].text == '无' or current_tr.find_by_tag('td')[self.seat_type_index].text == '候补':
                                    print(current_tr.find_by_tag('td')[0].text)
                                    print('无此座位类型出售!')
                                    continue
                            if current_tr.find_by_tag('td')[self.seat_type_index].text<len(self.passengers)  :
                                    print('票数不够!')                            
                            else:
                                    # 有票，尝试预订
                                    print('刷到票了（余票数：' + str(current_tr.find_by_tag('td')[self.seat_type_index].text) + '），开始尝试预订……')
                                    current_tr.find_by_css('td.no-br>a')[0].click()
                                    key_value = 1
                                    # 等待页面加载完毕
                                    self.wait_time('normalPassenger_' +str(int(key_value-1)))

                                    for p in self.passengers:
                                        # 选择用户
                                        print('开始选择用户……')
                                        self.driver.find_by_text(p).last.click()
                                        # 选择座位类型
                                        print('开始选择席别……')
                                        if self.seat_type_value != 0:
                                            sleep(1)
                                            seat_select = self.driver.find_by_id("seatType_" + str(key_value))[0]
                                            seat_select.find_by_xpath("//option[@value='" + str(self.seat_type_value) + "']")[0].click()
                                        key_value += 1
                                        if p[-1] == ')':
                                            self.driver.find_by_id('dialog_xsertcj_ok').click()
                                        print('正在提交订单……')
                                        self.driver.find_by_id('submitOrder_id').click()
                                        self.wait_time('content_checkticketinfo_id')
                                        # 查看返回结果是否正常
                                        submit_false_info = self.driver.find_by_id('orderResultInfo_id')[0].text
                                        if submit_false_info != '':
                                            print(submit_false_info)
                                            self.driver.find_by_id('qr_closeTranforDialog_id').click()
                                            self.driver.find_by_id('preStep_id').click()
                                            continue
                                        print('正在确认订单……')
                                        # 等待加载完毕
                                        self.wait_time('qr_submit_id')
                                        self.driver.find_by_id('qr_submit_id').click()
                                        print('预订成功，请及时前往支付……')
                                        # 发送通知信息
                                        self.send_mail(self.receiver_email, '恭喜您，抢到票了，请及时前往12306支付订单！')
                                        self.send_sms(self.receiver_mobile, '恭喜您，抢到票了，请及时前往12306支付订单！')
                    else:
                        for current_tr in elems:
                            if(current_tr.text==''):
                                print('没票')
                                continue
                            else:
                                # 下标索引
                                print('判断车票是否存在')
                                if current_tr.find_by_tag('td')[self.seat_type_index].text == '--' or current_tr.find_by_tag('td')[self.seat_type_index].text == '无':
                                    print('无此座位类型出售!')
                                    continue
                                else:
                                    # 有票，尝试预订
                                    print('刷到票了（余票数：' + str(current_tr.find_by_tag('td')[self.seat_type_index].text) + '），开始尝试预订……')
                                    current_tr.find_by_css('td.no-br>a')[0].click()
                                    key_value = 1
                                    # 等待页面加载完毕
                                    self.wait_time('normalPassenger_' +str(int(key_value-1)))

                                    for p in self.passengers:
                                          # 选择用户
                                        print('开始选择用户……')
                                        self.driver.find_by_text(p).last.click()
                                        # 选择座位类型
                                        print('开始选择席别……')
                                        if self.seat_type_value != 0:
                                            seat_select = self.driver.find_by_id("seatType_" + str(key_value))[0]
                                            seat_select.find_by_xpath("//option[@value='" + str(self.seat_type_value) + "']")[0].click()
                                        key_value += 1
                                        if p[-1] == ')':
                                            self.driver.find_by_id('dialog_xsertcj_ok').click()
                                        print('正在提交订单……')
                                        self.driver.find_by_id('submitOrder_id').click()
                                        self.wait_time('content_checkticketinfo_id')
                                        # 查看返回结果是否正常
                                        submit_false_info = self.driver.find_by_id('orderResultInfo_id')[0].text
                                        if submit_false_info != '':
                                            print(submit_false_info)
                                            self.driver.find_by_id('qr_closeTranforDialog_id').click()
                                            self.driver.find_by_id('preStep_id').click()
                                            continue
                                        print('正在确认订单……')
                                        # 等待加载完毕
                                        self.wait_time('qr_submit_id')
                                        self.driver.find_by_id('qr_submit_id').click()
                                        print('预订成功，请及时前往支付……')
                                        # 发送通知信息
                                        self.send_mail(self.receiver_email, '恭喜您，抢到票了，请及时前往12306支付订单！')
                                        self.send_sms(self.receiver_mobile, '恭喜您，抢到票了，请及时前往12306支付订单！')
                                        
                    # self.driver.quit()
                    continue
                except Exception as error_info:
                    print(error_info)
        except Exception as error_info:
            print(error_info)

    def wait_time(self, name):
            while self.driver.is_element_present_by_id(name) == False:
                 sleep(1)


    def send_sms(self, mobile, sms_info):
        """发送手机通知短信，用的是-互亿无线-的测试短信"""
        host = "106.ihuyi.com"
        sms_send_uri = "/webservice/sms.php?method=Submit"
        account = "C59782899"
        pass_word = "19d4d9c0796532c7328e8b82e2812655"
        params = parse.urlencode(
            {'account': account, 'password': pass_word,
                'content': sms_info, 'mobile': mobile, 'format': 'json'}
        )
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib2.HTTPConnectionWithTimeout(host, port=80, timeout=30)
        conn.request("POST", sms_send_uri, params, headers)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str

    def send_mail(self, receiver_address, content):
        """发送邮件通知"""
        # 连接邮箱服务器信息
        host = 'smtp.qq.com' #QQ
        sender = '673615750@qq.com'  # 你的发件邮箱号码
        pwd = '授权码'  # 不是登陆密码，是客户端授权密码
        # 发件信息
        receiver = receiver_address
        body = '<h2>温馨提醒：</h2><p>' + content + '</p>'
        msg = MIMEText(body, 'html', _charset="utf-8")
        msg['subject'] = '抢票成功通知！'
        msg['from'] = sender
        msg['to'] = receiver
        s = smtplib.SMTP(host, port=465, timeout=30)
        # 开始登陆邮箱，并发送邮件
        s.login(sender, pwd)
        s.sendmail(sender, receiver, msg.as_string())
        s.close()


if __name__ == '__main__':
    # 12306用户名
    # 12306登陆密码
    user_name = '18233121080'
    password = 'wo19911013'
    #user_name = 'shushe88639706'
    #password = 'plm20090105'
    # 乘客姓名
    passengers = '张益先,蔡进柯'
    # 乘车日期
    from_time = '2019-08-09'
   
    #发车时间
    train_date={
        #'00:00--24:00':'00002400',
        #'00:00--06:00':'00000600',
        #'06:00--12:00':'06001200',
        '12:00--18:00':'12001800',
        '18:00--24:00':'18002400',
    }

     # 城市cookie字典
    city_list = {'成都': '%u6210%u90FD%2CCDW',
                 '重庆': '%u91CD%u5E86%2CCQW',
                 '北京': '%u5317%u4EAC%2CBJP',
                 '广州': '%u5E7F%u5DDE%2CGZQ',
                 '杭州': '%u676D%u5DDE%2CHZH',
                 '宜昌': '%u5B9C%u660C%2CYCN',
                 '郑州': '%u90D1%u5DDE%2CZZF',
                 '深圳': '%u6DF1%u5733%2CSZQ',
                 '西安': '%u897F%u5B89%2CXAY',
                 '大连': '%u5927%u8FDE%2CDLT',
                 '武汉': '%u6B66%u6C49%2CWHN',
                 '上海': '%u4E0A%u6D77%2CSHH',
                 '南京': '%u5357%u4EAC%2CNJH',
                 '哈尔滨': '%u54C8%u5C14%u6EE8%2CHBB',
                 '海拉尔': '%u6D77%u62C9%u5C14%2CHRX',	
                 
                 '邯郸': '%u90AF%u90F8%2CHDP',	                 
                 '菏泽': '%u83CF%u6CFD%2CHIK',	
                 
                 '合肥': '%u5408%u80A5%2CHFH'}
    # 出发站
    from_station = city_list['哈尔滨']
    # 终点站
    to_station = city_list['海拉尔']
    # 座位类型
    seat_type = '软卧'
    # 抢票成功，通知该手机号码
    receiver_mobile = '15032862810'
    #抢票成功，通知该邮件
    receiver_email = '15032862810@163.com'
    # 开始抢票
    ticket = BrushTicket(train_date['18:00--24:00'],user_name, password, passengers.split(","), from_time, from_station,
                         to_station, seat_type, receiver_mobile, receiver_email,True)
    ticket.start_brush()