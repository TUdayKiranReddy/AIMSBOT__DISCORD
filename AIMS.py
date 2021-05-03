from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import cv2
import urllib
import base64
import pandas as pd
from captcha_decoder import *

class AIMS:
	def __init__(self):
		self.PATH = '/home/solomon/.imp_hid_data/chromedriver'
		self.url = 'https://aims.iith.ac.in/aims/'
		self.driver = webdriver.Chrome(self.PATH)
		self.maxAttempts = 3
		self.Nattemps = 0
		self.sCaptcha = None
		self.cData = None
		try:
			self.pData = pd.read_excel('Grades.xls')
		except:
			self.pData = None

	def homePage(self):
		self.driver.get(self.url)

	def getCaptcha1(self):
		captcha = self.driver.find_element_by_id("appCaptchaLoginImg")
		captcha_input = self.driver.find_element_by_id("captcha")
		captcha_text = captcha.get_attribute('src').split('/')[-1]

		return captcha_text, captcha_input

	def captcha_passer(self):

	    with open(r"captcha.png", 'wb') as f:
	        l = self.driver.find_element_by_xpath('//*[@alt="Captcha is being loaded"]')
	        f.write(l.screenshot_as_png)
	        f.close()

	    nd_nCaptcha = decode_captcha('captcha.png', imshow=False)
	    return nd_nCaptcha

	def click_captcha(self, text, captcha_input_element, captcha_submit_element):
		captcha_input_element.clear()
		self.driver.implicitly_wait(5)
		captcha_input_element.send_keys(text)
		captcha_submit_element.click()


	
	def getCaptcha2(self):
		nCaptcha_id = 'appCaptchaLoginImg'
		captchaRefreseh_id = 'loginCapchaRefresh'
		self.driver.implicitly_wait(5)

		nCaptcha = WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, "appCaptchaLoginImg"))
			)
		captchaRefreseh = WebDriverWait(self.driver, 10).until(
			EC.presence_of_element_located((By.ID, "loginCapchaRefresh"))
			)
		# nCaptcha = self.driver.find_element_by_id(nCaptcha_id)
		# captchaRefreseh = self.driver.find_element_by_id(captchaRefreseh_id)

		nCaptcha_src = nCaptcha.get_attribute('src')
		nCaptcha_input = self.driver.find_element_by_id('captcha')
		nCaptcha_submit = self.driver.find_element_by_id('submit')
		nCaptcha_refresh = self.driver.find_element_by_id('loginCapchaRefresh')

		loginHome = self.driver.current_url

		self.Nattemps = 1
		self.captcha_passer()
		self.driver.implicitly_wait(5)
		self.click_captcha(self.sCaptcha, nCaptcha_input, nCaptcha_submit)
		mainhome = self.driver.current_url

		if(loginHome == mainhome):
			return False
		else:
			return True

	def login(self, text=None, firstime=True):
		if firstime:
			self.homePage()
			self.driver.implicitly_wait(5)
			login = self.driver.find_element_by_id("uid")
			password = self.driver.find_element_by_id("pswrd")
			sign_in = self.driver.find_element_by_id("login")

			Captcha1 = self.getCaptcha1()
			login.send_keys("Your-USERID")
			password.send_keys("Your-Psswd")
			Captcha1[1].send_keys(Captcha1[0])
			sign_in.click()
			try:
				if self.driver.find_element_by_xpath('//*[@class="appMsgDiv"]'):
					print('Please wait for 30 minutes to proceed')
					return 2
			except:
				print('Cleared first Captcha!')

				self.sCaptcha = self.captcha_passer()
				if self.getCaptcha2():
					print('Cleared secound captcha, Now into AIIMS home page.')
					return 1
		else:
			self.sCaptcha = text
			if self.getCaptcha2():
				return 1
			else:
				print('Enter the correct Captcha text.')
				return 0

	def click_on_acad(self):
		Acad = self.driver.find_element_by_xpath('//*[@title="Academic"]')
		Acad.click()
		self.driver.implicitly_wait(2)

	def click_on_VmC(self):
		VmC = self.driver.find_element_by_xpath('//*[@title="View My Courses"]')
		VmC.click()
		self.driver.implicitly_wait(5)

	def GradeMaps(self, Grade):
	    nGrade = []
	    for i in Grade:
	        if i == 'A' or i=='A+':
	            nGrade.append(10)
	        elif i == 'A-':
	            nGrade.append(9)
	        elif i == 'B':
	            nGrade.append(8)
	        elif i == 'B-':
	            nGrade.append(7)
	        elif i == 'C':
	            nGrade.append(6)
	        elif i == 'C-':
	            nGrade.append(5)
	        elif i == 'D':
	            nGrade.append(4)
	        else:
	            nGrade.append(0)
	    return nGrade

	def cgpa(self):
	    data = self.cData[self.cData['Grade']!='S']
	    gp = data['GradePoints'].to_numpy(dtype='int')
	    cred = data['Credits'].to_numpy(dtype='float')
	    mask = data['Type']!='Additional'
	    Cred = cred[mask]
	    Gp = gp[mask]
	    return np.dot(Cred, Gp)/np.sum(Cred)

	def get_CGPA(self):
		self.click_on_acad()
		self.click_on_VmC()
		sems = self.driver.find_element_by_xpath('//*[@class="subCnt"]')
		gpas = sems.find_elements_by_xpath('//*[@class="col8 col"]')
		courseId = []
		courseName = []
		nCredits = []
		Type = []
		Grade = []

		for i in range(len(gpas)):
		    if gpas[i].text != ' ':
		        Id = sems.find_elements_by_xpath('//*[@class="col1 col"]')[i]
		        coursename = sems.find_elements_by_xpath('//*[@class="col2 col"]')[i]
		        ncredits = sems.find_elements_by_xpath('//*[@class="col3 col"]')[i]
		        typeofCourse = sems.find_elements_by_xpath('//*[@class="col5 col"]')[i]
		        typeofCourse = typeofCourse.text
		        if typeofCourse == ' Departmental Core Theory' or typeofCourse == ' Basic Sciences' or typeofCourse ==' Departmental Core Laboratory' or typeofCourse == ' Basic Engineering Skills':
		            Type.append('Core')
		        elif typeofCourse == ' Liberal Arts Elective':
		            Type.append('LA')
		        elif typeofCourse == ' Creative Arts':
		            Type.append('CA')
		        elif typeofCourse == ' Additional':
		            Type.append('Additional')
		        elif typeofCourse == ' Free Elective':
		            Type.append('Free Elective')
		        elif typeofCourse == ' Dept. Elective':
		            Type.append('Dept. Elective')
		        courseId.append(Id.text)
		        courseName.append(coursename.text)
		        nCredits.append((ncredits.text).replace(" ", ""))
		        
		        Grade.append((gpas[i].text).replace(" ", ""))
		Data = pd.DataFrame({'Course':courseId, 'Course Title':courseName, 'Credits':nCredits, 'Type':Type, 'Grade':Grade, 'GradePoints':self.GradeMaps(Grade)})
		Data=Data[~Data.duplicated(['Course'])]
		Data.to_excel("Grades.xls", index=False)
		if self.pData is None:
			self.pData = Data.copy()

		self.cData = Data.copy()
		return self.cgpa()

	def any_new_grade(self):
		# if not self.cData.equals(self.pData):
		# 	df = self.cData.merge(self.pData, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
		# 	return df
		# else:
		# 	return None
		flag = False
		ct =[]
		g = []
		for i in range(len(self.cData['Course Title'])):
			for j in range(len(self.pData['Course Title'])):
				if self.cData['Course Title'].iloc[i]==self.pData['Course Title'].iloc[j]:
					flag|=True
					break
				else:
					flag|=False
			if not flag:
				ct.append(self.cData['Course Title'].iloc[i])
				g.append(self.cData['Grade'].iloc[i])
		if len(ct) != 0:
			df = pd.DataFrame({'Course Title':ct, 'Grade':g})
		else:
			df = pd.DataFrame({})
		return df
	def logout(self):
		dropdown = self.driver.find_element_by_id('appUName')
		dropdown.click()
		self.driver.implicitly_wait(2)
		logoutBtn = self.driver.find_element_by_xpath('//*[@title="Logout"]')
		logoutBtn.click()
