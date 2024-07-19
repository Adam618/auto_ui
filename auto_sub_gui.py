# coding=utf-8
# @Author :djp
# @Time :2022/4/21 16:07
# @File :auto_sub_gui.py
# @software: PyCharm

import os
import shutil
import random
import time
import muggle_ocr
from datetime import datetime, timedelta, date
import cv2 as cv
import pytesseract
from PIL import Image
import requests
from hashlib import md5
import pandas as pd
import pyautogui
from msedge.selenium_tools import Edge
from msedge.selenium_tools import EdgeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.common.keys as keys


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def PostPic_base64(self, base64_str, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
            'file_base64': base64_str
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


class work_order:

    @staticmethod
    def find_yzm(image):
        # 边缘保留滤波  去噪
        dst = cv.pyrMeanShiftFiltering(image, sp=10, sr=150)
        # 灰度图像
        gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
        # 二值化
        ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
        # 形态学操作   腐蚀  膨胀
        erode = cv.erode(binary, None, iterations=2)
        dilate = cv.dilate(erode, None, iterations=1)
        cv.imshow('dilate', dilate)
        # 逻辑运算  让背景为白色  字体为黑  便于识别
        cv.bitwise_not(dilate, dilate)
        cv.imshow('binary-image', dilate)
        # 识别
        test_message = Image.fromarray(dilate)
        text = pytesseract.image_to_string(test_message)
        return {text}

    @staticmethod
    def save_img():
        rdm_status = random.randint(0, 10000)
        # 截取当前网页并放到E盘下命名为printscreen，该网页有我们需要的验证码
        driver.save_screenshot("img/my_screen_" + str(rdm_status) + ".png")
        imgelement = driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div[3]/img')  # 定位验证码
        location = imgelement.location  # 获取验证码x,y轴坐标
        size = imgelement.size  # 获取验证码的长宽
        rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                  int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
        i = Image.open("img/my_screen_" + str(rdm_status) + ".png")  # 打开截图
        frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
        frame4 = frame4.convert("RGB")
        frame4.save("img/yzm_" + str(rdm_status) + ".jpg")  # 保存我们接下来的验证码图片 进行打码
        print(rdm_status)
        return rdm_status

    @staticmethod
    def get_code1(rdm_status):
        # sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)
        # # ModelType.OCR 可识别光学印刷文本 这里个人觉得应该是官方文档写错了 官方文档是ModelType.Captcha 可识别光学印刷文本
        # with open("img/yzm_" + str(rdm_status) + ".jpg", 'rb') as f:
        #     b = f.read()
        # text = sdk.predict(image_bytes=b)
        # print("新验证码1", text)

        # ModelType.Captcha 可识别4-6位验证码
        sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
        with open("img/yzm_" + str(rdm_status) + ".jpg", 'rb') as f:
            b = f.read()
        text = sdk.predict(image_bytes=b)
        print("新验证码2", text)

    @staticmethod
    def get_code(rdm_status):
        chaojiying = Chaojiying_Client('djp4992', 'djp123456', '935864')  # 用户中心>>软件ID 生成一个替换 96001
        im = open("img/yzm_" + str(rdm_status) + ".jpg", 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        rs_json = chaojiying.PostPic(im, 1902)
        rs = rs_json["pic_str"]
        return rs

    @staticmethod
    def del_match_file(path):
        before_yesterday_str = (date.today() + timedelta(days=-2)).strftime("%d")
        del_list = []
        for dirs, name, file in os.walk(path):
            for i in file:
                if ("chunks_" + before_yesterday_str) in str(i):
                    del_list.append(dirs + '\\' + i)
        for i in del_list:
            os.remove(i)
        return

    @staticmethod
    def del_chgfnm(path1, path2):
        # desktop_path, submit_path
        # path1:需要在桌面删除的文件路径
        tmp_df = pd.DataFrame([1, 2, 3])
        filename1 = 'visit_inquiry.xlsx'
        file_path1 = os.path.join(path1, filename1)
        # path2:生成提交文件的文件夹
        path_list = os.listdir(path2)
        # path_list.sort(key=lambda x: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(x))))
        path_list.sort()
        if len(path_list) == 0:
            print("无提交文件")
            pass
        else:
            filename2 = path_list[0]
            file_path2 = os.path.join(path2, filename2)
            shutil.move(file_path2, file_path1)
        return

    @staticmethod
    def all_control(submit_path, driver, define):
        global l
        work_order.first_submit(driver)
        if define == 0:
            l = len(os.listdir(submit_path))
            print("文件数目:", l)
            work_order.del_chgfnm(desktop_path, submit_path)
        elif define == 1:
            print("提交之前的最后一个")
            if len(os.listdir(submit_path)) == 0:
                l = 1
        time.sleep(delay_time - 2)
        current_windows = driver.window_handles
        driver.switch_to.window(current_windows[-1])
        work_order.second_submit(driver)
        # 非空时
        while l > 0:
            work_order.del_chgfnm(desktop_path, submit_path)
            current_windows = driver.window_handles
            driver.switch_to.window(current_windows[-1])
            work_order.second_submit(driver)
            l = l - 1
        time.sleep(delay_time * 2)
        driver.quit()

    @staticmethod
    def first_submit(driver):
        # 打开OA页面
        driver.get("http://sd-oa.bf.ctc.com/login.html#")
        time.sleep(5)
        # 设置全屏
        driver.maximize_window()
        # 输入账号密码
        driver.find_element(by=By.NAME, value='userid').send_keys(oa_name)
        driver.find_element(by=By.NAME, value='password').send_keys(oa_pw)
        rdm_status = work_order.save_img()
        # 超级鹰
        rs1 = work_order.get_code(rdm_status)
        print(rs1)

        # work_order.get_code1(rdm_status)

        # cv
        # img_src = cv.imread(r'img/yzm.jpg')
        # rs2 = work_order.find_yzm(img_src)
        # print("cv2", rs2)

        driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div[1]/div[3]/input').send_keys(rs1)
        time.sleep(delay_time)
        # 点击登录
        driver.find_element(by=By.ID, value='submit').click()
        time.sleep(delay_time - 2)
        try:
            M = 0
            while M < 3:
                boolname = driver.find_element(by=By.XPATH, value='/html/body/div[5]/div').text
                print(boolname)
                if boolname == "图片验证码错误！":
                    print("识别失败")
                    rdm_status = work_order.save_img()
                    rs1 = work_order.get_code(rdm_status)
                    print("失败后的", rs1)
                    driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div[1]/div[3]/input').clear()
                    time.sleep(delay_time - 3)
                    driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div[1]/div[3]/input').send_keys(rs1)
                    # 点击登录
                    driver.find_element(by=By.ID, value='submit').click()
                    M = M + 1
        except:
            # 打开一个新窗口打开ITSM
            js = 'window.open("http://sd-oa.bf.ctc.com/cms-api/ssoApi/ssoTo?appCode=jtitwg");'
            driver.execute_script(js)
            time.sleep(delay_time + 2)
        # try:
        #     rdm_status = work_order.save_img()
        #     rs1 = work_order.get_code(rdm_status)
        #     driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div[1]/div[3]/input').send_keys(rs1)
        #     # 点击登录
        #     driver.find_element(by=By.ID, value='submit').click()
        #     time.sleep(delay_time)
        #     boolname = driver.find_element(by=By.XPATH, value='//*[@id="J_common_header_menu"]/li[1]/span').text
        #     print(boolname)
        #     if boolname == '首页':
        #         js = 'window.open("http://sd-oa.bf.ctc.com/cms-api/ssoApi/ssoTo?appCode=jtitwg");'
        #         driver.execute_script(js)
        #         time.sleep(delay_time + 2)
        # except:
        #     m = 0
        #     while m < 3:
        #         print("识别失败")
        #         rdm_status = work_order.save_img()
        #         rs1 = work_order.get_code(rdm_status)
        #         print("失败后的", rs1)
        #         driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div[1]/div[3]/input').clear()
        #         time.sleep(delay_time - 2)
        #         driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div[1]/div[3]/input').send_keys(rs1)
        #         print("22")
        #         # 点击登录
        #         driver.find_element(by=By.ID, value='submit').click()
        #         boolname = driver.find_element(by=By.XPATH, value='//*[@id="J_common_header_menu"]/li[1]/span').text
        #         m = m + 1
        #         if boolname == '首页':
        #             m = 3
        #     # 打开一个新窗口打开ITSM
        #     js = 'window.open("http://sd-oa.bf.ctc.com/cms-api/ssoApi/ssoTo?appCode=jtitwg");'
        #     driver.execute_script(js)
        #     time.sleep(delay_time + 2)

    @staticmethod
    def second_submit(driver):
        # 打开一个新窗口打开提交电子工单界面
        js2 = 'window.open("http://10.128.86.199:7006/jtitsmForm/jtitsmVisitInquiry/index?flowMod=16205&callback=refresh");'
        driver.execute_script(js2)
        time.sleep(delay_time - 3)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(delay_time)
        # 输入所需内容
        driver.find_element(by=By.CLASS_NAME, value='el-input__inner').send_keys('到访地查询问题协查-山东')
        time.sleep(delay_time - 2)
        driver.find_element(by=By.CLASS_NAME, value='el-textarea__inner').send_keys('请集团领导协查处理')
        time.sleep(delay_time - 2)
        element = driver.find_element(by=By.CLASS_NAME, value='el-upload__input')
        filename1 = "号码清单.xlsx"
        sub_path1 = os.path.join(os.path.join(desktop_path, filename1))
        element.send_keys(sub_path1)
        driver.find_element(by=By.XPATH,
                            value='/html/body/div/div/form/div[1]/div[1]/div/div[4]/div[2]/div/div[1]/button[1]').click()
        element = driver.find_element(by=By.XPATH,
                                      value='/html/body/div[1]/div/form/div[1]/div[1]/div/div[4]/div[2]/div/div[3]/div/div/div/div/div[2]/div/div[1]/input')  # 定位到上传文件框
        filename2 = "visit_inquiry.xlsx"
        sub_path2 = os.path.join(os.path.join(desktop_path, filename2))
        element.send_keys(sub_path2)
        driver.find_element(by=By.XPATH,
                            value='/html/body/div[1]/div/form/div[1]/div[1]/div/div[4]/div[2]/div/div[3]/div/div/div/div/div[2]/div/button').click()
        time.sleep(delay_time)
        driver.find_element(by=By.XPATH, value='//*[@id="220001"]').click()
        time.sleep(delay_time)
        driver.find_element(by=By.XPATH,
                            value='//*[@id="visitInquiryForm"]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div/div[2]/ul/li[1]/a').click()
        time.sleep(delay_time)
        driver.find_element(by=By.XPATH,
                            value='//*[@id="visitInquiryForm"]/div/div[2]/div/div[3]/div/button[2]').click()
        time.sleep(delay_time * 2)


if __name__ == '__main__':

    oa_name = 'liutl'
    oa_pw = 'DukY#419'
    # 页面时间
    delay_time = 5
    type = input("是否提交之前的最后一个:")
    if str(type) == "1":
        define = 1
    else:
        define = 0

    (screenWidth, screenHeight) = pyautogui.size()
    if (screenWidth, screenHeight) == (2880, 1920):
        desktop_path = r'C:\Users\18493\Desktop'
    elif (screenWidth, screenHeight) == (2560, 1440):
        desktop_path = r'C:\Users\djp\Desktop'
    elif (screenWidth, screenHeight) == (2560, 1600):
        desktop_path = r'D:\software'
    else:
        desktop_path = r'C:\Users\Administrator\Desktop'
    submit_path = "submit_data"
    backupdir = "backup"
    while True:

        now_hour = datetime.now().hour
        if 18 <= now_hour <= 22:
            sleep_time = 600
        elif now_hour > 22 or now_hour < 6:
            sleep_time = 1200
        else:
            sleep_time = 300
        if int(now_hour) == 0:
            work_order.del_match_file(backupdir)
        if int(now_hour) == 9:
            work_order.del_match_file(backupdir)
        str_day_now = datetime.now().strftime('%Y%m%d%H%M')
        print("现在时间", str_day_now)
        # 工单提交
        l = len(os.listdir(submit_path))

        if str(type) == "1" and l == 0:
            l = 1
        if l > 0:
            # Edge浏览器
            edge_options = EdgeOptions()
            edge_options.use_chromium = True
            # 设置无界面模式，也可以添加其它设置
            # edge_options.add_argument('headless')
            edge_options.add_argument("--disable-gpu")
            (screenWidth, screenHeight) = pyautogui.size()
            if (screenWidth, screenHeight) == (2560, 1600):
                driver = webdriver.Edge()
                # driver = Edge(executable_path="MicrosoftWebDriver.exe", options=edge_options)
            else:
                driver = Edge(executable_path="msedgedriver.exe", options=edge_options)
            work_order.all_control(submit_path, driver, define)
            define = 0
        print("处理完毕")
        time.sleep(sleep_time)
