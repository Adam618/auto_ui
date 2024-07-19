from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.common.exceptions import NoAlertPresentException
import unittest
import time
import ddddocr
from PIL import Image


# 填充固定表单
def fill_general_info(driver, name, pwd):
    driver.find_element(By.NAME, "userName").click()
    driver.find_element(By.NAME, "userName").send_keys(name)
    driver.find_element(By.NAME, "password").click()
    driver.find_element(By.NAME, "password").send_keys(pwd)


# 执行ocr识别操作，识别成功则返回True
def apply_ocr(driver):
    time.sleep(2)
    captcha_element = driver.find_element(By.XPATH, '//*[@id="imageCaptcha"]/img')
    captcha_element.click()
    time.sleep(2)
    captcha_element.screenshot('temp.png')
    captcha_image = Image.open('temp.png')
    width, height = captcha_image.size

    # 计算主体裁剪区域，只保留左侧2/3部分
    crop_area = (0, 0, width * 3 // 5, height)
    cropped_image = captcha_image.crop(crop_area)

    # 添加时间戳
    # timestamp = time.strftime("%Y%m%d_%H%M%S")
    # 保存裁剪后的图片，文件名包含时间戳
    # cropped_image.save(f"captcha_{timestamp}.png")

    ocr = ddddocr.DdddOcr()
    ocr.set_ranges("0123456789+-x/=")
    # OCR识别
    result = ocr.classification(cropped_image)
    # 提取操作数和运算符
    print(result)
    # 检查是否识别正确
    operators = "+-x/="
    # 识别结果大于3位且第2位有算术操作符才会进行下一步
    if len(result) > 2 and result[1] in operators:
        operand1 = int(result[0])
        operator = result[1]
        operand2 = int(result[2:])
        # 使用字典映射运算符
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            'x': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else '除数不能为0'
        }
        # 计算结果
        value = operations[operator](operand1, operand2)
        # 输入计算结果到表单
        captcha_input_box = driver.find_element(By.XPATH, '//*[@id="imageCaptcha"]/div/input')
        captcha_input_box.clear()
        captcha_input_box.send_keys(value)
        return True
    else:
        return False


# 获取短信验证码相关操作
def get_sms_code(driver):
    driver.find_element(By.XPATH, "//*[@id='captcha']/span").click()
    time.sleep(2)
    # 点击获取短信验证码之后，会验证图片验证码是否输入正确，如果不正确则需要重新识别
    # captcha_error = driver.find_elements(By.XPATH, '//*[@id = "imgCaptchaError"')

    # if len(captcha_error) != 0:
    #     print("!!!!!!!!!!!!!!")
    #     apply_ocr(driver)
    # try:
    #     captcha_error = driver.find_elements(By.ID, 'imgCaptchaError')
    #
    #     if len(captcha_error) != 0:
    #         print("!!!!!!!!!!!!!!")
    #         apply_ocr(driver)
    # except InvalidSelectorException as e:
    #     pass

    # driver.find_element(By.XPATH, "//div[@id='app']/div/div[2]/div/div[2]/form/div[10]/button").click()

    time.sleep(15)
    pass


# 登录页相关操作
def login_process(driver):
    # 固定表单信息
    name = "19953199425"
    pwd = "Caoyang5115236"

    driver.get("http://10.143.28.206:23007/portal/#/login")
    fill_general_info(driver, name, pwd)

    status = apply_ocr(driver)
    if not status:
        apply_ocr(driver)

    # 待完成，返回状态码后进行下一步
    get_sms_code(driver)


# 登录页之后的操作
def task_process():
    pass


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Edge()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_app_dynamics_job(self):
        driver = self.driver
        # 登录操作
        login_process(driver)
        # 登录完成跳转
        driver.find_element(By.XPATH, "//div[@id='app']/div/div[2]/div/div[2]/form/div[10]/button").click()
        time.sleep(2000)
        # 登录后续操作，待完成
        task_process()


if __name__ == "__main__":
    unittest.main()
