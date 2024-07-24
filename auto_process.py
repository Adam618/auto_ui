from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
import time
import ddddocr
import pickle
from PIL import Image
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 参数设置
MAX_OCR_NUM = 10  # OCR最大重新识别次数
NAME = "19953199425"  # 用户名
PWD = "Caoyang5115236"  # 密码
# NAME = "17353462690"  # 用户名
# PWD = "dbq$LoDgBoi"  # 密码


def fill_general_info(driver, NAME, PWD):
    """
    填充用户名、密码固定表单
    :param driver:
    :param name: 用户名
    :param pwd:  密码
    :return:
    """
    driver.find_element(By.NAME, "userName").click()
    driver.find_element(By.NAME, "userName").send_keys(NAME)
    driver.find_element(By.NAME, "password").click()
    driver.find_element(By.NAME, "password").send_keys(PWD)



def apply_ocr(driver, is_first=False):
    """
    # 对算术验证码执行ocr识别操作，识别成功则返回True
    :param driver:
    :param is_first: 是否第一次识别（第一次识别不需要刷新验证码）
    :return:
    """
    captcha_element = driver.find_element(By.XPATH, '//*[@id="imageCaptcha"]/img')
    if not is_first:
        time.sleep(2)
        captcha_element.click()
    time.sleep(2)
    captcha_element.screenshot('temp.png')
    captcha_image = Image.open('temp.png')
    width, height = captcha_image.size

    # 对验证码主题区域裁剪（只保留左侧2/3部分）
    crop_area = (0, 0, width * 3 // 5, height)
    cropped_image = captcha_image.crop(crop_area)
    # 添加时间戳
    ocr = ddddocr.DdddOcr()
    ocr.set_ranges("0123456789+-x/=")
    # OCR识别
    result = ocr.classification(cropped_image)
    # 提取操作数和运算符
    print("算术验证码识别结果：", result)
    # 检查是否识别正确
    operators = "+-x/="
    # 识别结果大于3位且第2位有算术操作符才会进行下一步
    if len(result) == 3 and result[1] in operators:
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


def get_sms_code(driver):
    """
    目前为手动输入短信验证码
    :param driver:
    :return:
    """
    driver.find_element(By.XPATH, "//*[@id='captcha']/span").click()
    sms_captcha_input_box = driver.find_element(By.XPATH, "//*[@id='captcha']/div/input")
    sms_captcha_input_box.click()
    sms_captcha_input_box.clear()
    time.sleep(2)

# 登录页相关操作
def login_process(driver):
    """
    登录页的相关操作，操作成功后跳转综调首页
    :param driver:
    :return:
    """
    # 固定表单信息
    driver.get("http://10.143.28.206:23007/portal/#/login")
    fill_general_info(driver, NAME, PWD)
    status = apply_ocr(driver, is_first=True)
    for i in range(MAX_OCR_NUM):
        if status:
            break
        status = apply_ocr(driver)
    get_sms_code(driver)


def check_and_click(driver):
    """
    寻找首页固定“网络数据管理平台”字段，执行自动处理相关操作。
    :param driver:
    :return:
    """
    original_window = driver.current_window_handle
    try:
        wait = WebDriverWait(driver, 10)

        # 打开首页并点击tab
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='tab-0']"))).click()

        # 点击目标元素
        target_element = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'gc-sch-wait-item-title') and contains(text(), '网络数据管理平台')]")
            )
        )
        target_element.click()
        time.sleep(5)

        # 获取当前窗口句柄
        # 切换到新窗口
        for handle in driver.window_handles:
            if handle != original_window:
                driver.switch_to.window(handle)
                break
        time.sleep(5)
        # 执行新页面上的操作
        driver.find_element(By.ID, "dialog").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "//textarea").click()
        time.sleep(2)
        driver.find_element(By.XPATH, "//textarea").clear()
        time.sleep(2)
        driver.find_element(By.XPATH, "//textarea").send_keys("已通知源端处理")
        time.sleep(2)
        driver.find_element(By.XPATH, "//input[@type='text']").clear()
        time.sleep(2)
        driver.find_element(By.XPATH, "//input[@type='text']").send_keys(u"孙国标")
        time.sleep(2)
        driver.find_element(By.XPATH,
            u"(.//*[normalize-space(text()) and normalize-space(.)='确定'])[2]/following::div[5]").click()
        time.sleep(2)
        # 确定按钮
        driver.find_element(By.XPATH, u"(.//*[normalize-space(text()) and normalize-space(.)='取消'])[3]/following::span[1]").click()
        print("工单转发成功！")
        time.sleep(5)
        driver.close()
        return True  # Indicate that the target element was found and clicked
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)
        driver.close()
        print("没有工单或者工单转发失败！")
        return False  # Indicate that the target element was not found


def task_process(driver):
    """
    登录之后的操作，无限循环刷新
    :param driver:
    :return:
    """
    start_time = time.time()  # 记录开始时间
    while True:
        check_and_click(driver)
        current_time = time.time()
        run_time = current_time - start_time
        run_minutes, run_seconds = divmod(run_time, 60)
        run_hours, run_minutes = divmod(run_minutes, 60)
        print(f"程序已运行 {int(run_hours):02d}:{int(run_minutes):02d}:{int(run_seconds):02d}")
        time.sleep(300)  # Wait for 5 minutes before refreshing
        driver.refresh()


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Edge()
        self.driver.implicitly_wait(60)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_app_dynamics_job(self):
        """
        主进程
        :return:
        """

        driver = self.driver
        driver.maximize_window()
        # 登录操作
        login_process(driver)
        # 手动短信验证码预留时间
        time.sleep(30)
        # 登录完成跳转
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div/div[2]/form/div[10]/button').click()
        time.sleep(5)
        task_process(driver)


if __name__ == "__main__":
    unittest.main()
