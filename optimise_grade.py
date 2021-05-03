import cvxpy as cp
import numpy as np
import pandas as pd

def dot(npvec, cpvec):
	x = 0
	for i in range(len(npvec)):
		x += npvec[i]*cpvec[i]
	return x

def cgpa(Data):
	    data = Data[Data['Grade']!='S']
	    gp = data['GradePoints'].to_numpy(dtype='int')
	    cred = data['Credits'].to_numpy(dtype='float')
	    mask = data['Type']!='Additional'
	    Cred = cred[mask]
	    Gp = gp[mask]
	    return np.dot(Cred, Gp)/np.sum(Cred)

def optimise_grade(Data, minLA=0, minCA=0, minFE=0, minDE=0, minCred=None):

	data = Data[Data['Grade']!='S']

	gp = data['GradePoints'].to_numpy(dtype='int')
	cred = data['Credits'].to_numpy(dtype='float')

	mask = data['Type']=='Core'
	nCore = np.sum(cred[mask])
	Tcore = np.sum(np.dot(gp[mask] ,cred[mask]))

	LAs =  data['Type']=='LA'
	CAs =  data['Type']=='CA'
	FEs = data['Type']=='Free Elective'
	#DEs = data['Type']=='Dept. Elective'
	AEs = data['Type']=='Additional'

	Ln = data[LAs]
	Cn = data[CAs]
	Fn = data[FEs]
	#Dn = data[DEs]
	An = data[AEs]

	Lg = gp[LAs]
	Cg = gp[CAs]
	Fg = gp[FEs]
	#Dg = gp[DEs]
	Ag = gp[AEs]

	nLA = cred[LAs]
	nCA = cred[CAs]
	nFE = cred[FEs]
	#nDE = cred[DEs]
	nAE = cred[AEs]
	


	l = cp.Variable((len(Ln), ), boolean=True)
	c = cp.Variable((len(Cn), ), boolean=True)
	f = cp.Variable((len(Fn), ), boolean=True)
	#d = cp.Variable((len(Dn), ), boolean=True)
	a = cp.Variable((len(An), ), boolean=True)

	if minCred == None:
		minCred = nCore + minLA + minCA + minFE + minDE

	NLAs = dot(nLA, l)
	NCAs = dot(nCA, c)
	NFEs = dot(nFE, f)
	#NDEs = dot(nDE, d)
	NAEs = dot(nAE, a)
	
	nCredits = nCore + NLAs + NCAs + NFEs  + NAEs

	gpa = (Tcore + dot(nLA*Lg, l) + dot(nCA*Cg, c) + dot(nFE*Fg, f)  + dot(nAE*Ag, a))/nCredits # addd  dot(nDE*Dg, d)
	constraints = [nCredits >= minCred, NLAs >= minLA, NCAs >= minCA, NFEs + NAEs >= minFE]#, NDEs >= minDE]

	problem  = cp.Problem(cp.Minimize(-1*gpa), constraints)

	problem.solve(solver='ECOS_BB', qcp=True)

	L = [(i>0.5) for i in l.value]
	C = [(i>0.5) for i in c.value]
	F = [(i>0.5) for i in f.value]
	#D = [(i>0.5) for i in d.value]
	A = [(i>0.5) for i in a.value]

	cLAs = Ln[L]
	cCAs = Cn[C]
	cFEs = Fn[F]
	#cDEs = Dn[D]
	cAEs = An[A]
	s = 'To Maximize your grade do the following conversions:-\n'
	s += ('Convert the following Additional into Electives:-\n')
	for i in range(np.sum(A)):
		s += ('--> '+cAEs['Course'].iloc[i]+cAEs['Course Title'].iloc[i]+'\n')

	s += ('\n\nConvert the following Electives into Additional:-\n')
	for i in range(np.sum(np.logical_not(L))):
		s += ('--> '+Ln[np.logical_not(L)]['Course'].iloc[i]+ Ln[np.logical_not(L)]['Course Title'].iloc[i]+'\n') 
	for i in range(np.sum(np.logical_not(C))):
		s += ('--> '+Cn[np.logical_not(C)]['Course'].iloc[i]+ Cn[np.logical_not(C)]['Course Title'].iloc[i]+'\n') 
	for i in range(np.sum(np.logical_not(F))):
		s += ('--> '+Fn[np.logical_not(F)]['Course'].iloc[i]+ Fn[np.logical_not(F)]['Course Title'].iloc[i]+'\n') 
	# for i in range(np.sum(np.logical_not(D)):
	# 	s += ('--> '+Dn[np.logical_not(D)]['Course'].iloc[i]+ Dn[np.logical_not(D)]['Course Title'].iloc[i]+'\n') 
	s += ('\nBefore:-\n')
	s += ('CGPA:- '+ str(np.round(cgpa(Data), 3))+'\n')
	s += ('Credits:-  '+ str(int(np.sum(data['Credits'][data['Type']!='Additional'].to_numpy(dtype='float'))))+'\n')
	s += ('\nAfter\n')
	s += ('CGPA:- '+ str(np.round(gpa.value, 3))+'\n')
	s += ('Credits:- '+ str(int(nCredits.value))+'\n')
	print(s)
	return s
if __name__=="__main__":
	Data = pd.read_excel('Grades.xls')
	optimise_grade(Data, minLA=0)