# -*- coding: utf-8 -*-
"""mimic 4 data processing itog.ipynb
#Загрузка данных
"""

import pandas as pd
from tqdm import tqdm
import json
import numpy as np

import warnings
warnings.filterwarnings('ignore')

basePath = "/content/drive/MyDrive/mimic4/"

d_icd_diagnoses = pd.read_csv(basePath+'d_icd_diagnoses.csv.gz')

d_icd_procedures = pd.read_csv(basePath+'d_icd_procedures.csv.gz')

d_labitems = pd.read_csv(basePath+'d_labitems.csv.gz')

diagnoses_icd = pd.read_csv(basePath+'diagnoses_icd.csv.gz')

patients = pd.read_csv(basePath+'patients.csv.gz')

procedures_icd = pd.read_csv(basePath+'procedures_icd.csv.gz')

admissions = pd.read_csv(basePath+'admissions.csv.gz')


"""#Вспомогательный функции для извлечения данных из таблиц"""

def getGender(subject_id):
  return patients[patients.subject_id == subject_id].gender.values[0]

def getAge(subject_id):
  return int(patients[patients.subject_id == subject_id].anchor_age.values[0])

def getLabLabel(itemid):
  return d_labitems[d_labitems.itemid == itemid].label.values[0]

def getLabFluid(itemid):
  return d_labitems[d_labitems.itemid == itemid].fluid.values[0]

def getLabCategory(itemid):
  return d_labitems[d_labitems.itemid == itemid].category.values[0]

def getDiagnosesData(subject_id, hadm_id):
  subDiagnoses = diagnoses_icd[(diagnoses_icd.subject_id == subject_id) & (diagnoses_icd.hadm_id == hadm_id)]
  return {'diagnoses_icd_code': list(subDiagnoses.icd_code), 'diagnoses_icd_version':list(subDiagnoses.icd_version)}

def getProcedureData(subject_id, hadm_id):
  subProcedures = procedures_icd[(procedures_icd.subject_id == subject_id) & (procedures_icd.hadm_id == hadm_id)]
  return {'procedures_icd_code ': list(subProcedures.icd_code), 'procedures_icd_version ':list(subProcedures.icd_version)}

def getAdmissionInformation(subject_id, hadm_id):
  subAdmissions = admissions[(admissions.subject_id == subject_id) & (admissions.hadm_id == hadm_id)]
  return {'admittime':list(subAdmissions.admittime)[0].split(' ')[0],
          'dischtime':list(subAdmissions.dischtime)[0].split(' ')[0],
          'death': 0 if subAdmissions.deathtime.isnull().values.any() else 1,
          'admission_type':list(subAdmissions.admission_type)[0]}

def getItemData(row):
  return row.itemid, {'lab_category': getLabCategory(row.itemid),
          'lab_fluid': getLabFluid(row.itemid),
          'lab_label': getLabLabel(row.itemid),
          'charttime':row.charttime,
          'storetime':row.storetime,
          'value':row.value,
          'valuenum':float(row.valuenum),
          'valueuom':row.valueuom,
          'ref_range_lower':float(row.ref_range_lower),
          'ref_range_upper':float(row.ref_range_upper),
          'flag': row.flag,
          'priority': row.priority}

"""#Извлечение данных"""

names = ['labevent_id',
 'subject_id',
 'hadm_id',
 'specimen_id',
 'itemid',
 'order_provider_id',
 'charttime',
 'storetime',
 'value',
 'valuenum',
 'valueuom',
 'ref_range_lower',
 'ref_range_upper',
 'flag',
 'priority']

listsForPandas = []
for i in names:
  listsForPandas.append([])

def formNewPatient(lab):
  subject_id = list(set(lab.subject_id))[0]
  newPatient = {}
  newPatient['subject_id'] = subject_id
  newPatient['gender'] = 0 if getGender(subject_id) == 'F' else 1
  newPatient['age'] = getAge(subject_id)
  hadmList = set(lab.hadm_id.dropna())
  hadmResult = {}
  for hadm_id in hadmList:
    newHadm = {}
    try:
      newHadm['diagnoses'] = getDiagnosesData(subject_id, hadm_id)
    except:
      global diagnosFail
      diagnosFail += 1
    try:
      newHadm['procedures'] = getProcedureData(subject_id, hadm_id)
    except:
      global procedureFail
      procedureFail += 1
    try:
      itemsDf = lab[(lab.hadm_id == hadm_id)]
      itemDict = {}
      for value in itemsDf.apply(getItemData, axis=1):
        itemDict[value[0]] = value[1]
      newHadm['items'] = itemDict
    except:
      global itemsFail
      itemsFail += 1
    try:
      newHadm['admission'] = getAdmissionInformation(subject_id, hadm_id)
    except:
      global admissionFail
      admissionFail += 1

    hadmResult[hadm_id] = newHadm

  try:
    hadmResult = dict(sorted(hadmResult.items(), key=lambda item: item[1]['admission']['admittime']))
    hadmResult['sorted'] = 1
  except:
    print('sort error')
    hadmResult['sorted'] = 0
  newPatient['hadms'] = hadmResult
  if (len(newPatient['hadms']) > 1):
      with open('/content/drive/MyDrive/mimic-patients/{}.json'.format(subject_id), 'w') as fp:
          json.dump(newPatient, fp)

def formNewPatient(lab):
  subject_id = list(set(lab.subject_id))[0]
  newPatient = {}
  newPatient['subject_id'] = subject_id
  newPatient['gender'] = 0 if getGender(subject_id) == 'F' else 1
  newPatient['age'] = getAge(subject_id)
  hadmList = set(lab.hadm_id.dropna())
  hadmResult = {}
  for hadm_id in hadmList:
    newHadm = {}
    try:
      newHadm['diagnoses'] = getDiagnosesData(subject_id, hadm_id)
    except:
      global diagnosFail
      diagnosFail += 1
    try:
      newHadm['procedures'] = getProcedureData(subject_id, hadm_id)
    except:
      global procedureFail
      procedureFail += 1
    try:
      itemsDf = lab[(lab.hadm_id == hadm_id)]
      itemDict = {}
      for value in itemsDf.apply(getItemData, axis=1):
        itemDict[value[0]] = value[1]
      newHadm['items'] = itemDict
    except:
      global itemsFail
      itemsFail += 1
    try:
      newHadm['admission'] = getAdmissionInformation(subject_id, hadm_id)
    except:
      global admissionFail
      admissionFail += 1

    hadmResult[hadm_id] = newHadm
  try:
    hadmResult = dict(sorted(hadmResult.items(), key=lambda item: item[1]['admission']['admittime']))
    hadmResult['sorted'] = 1
  except:
    print('sort error')
    hadmResult['sorted'] = 0
  newPatient['hadms'] = hadmResult
  if (len(newPatient['hadms']) > 1):
    # with open('/content/drive/MyDrive/mimic-patients/{}.json'.format(subject_id), 'w') as f:
    #     json.dump(newPatient, f)
    with open('{}.json'.format(subject_id), 'w') as f:
        json.dump(newPatient, f)


countLines_ = 0
diagnosFail = 0
procedureFail = 0
admissionFail = 0
itemsFail = 0
prevSubject_id = 10000032
lab = pd.DataFrame(columns=names)
with open(basePath+'labevents.csv') as f:
  f.readline()
  for i in tqdm(f):
    try:
      rawValues = i.strip().split(',')
      rawValues[0] = int(rawValues[0])
      rawValues[1] = int(rawValues[1])
      rawValues[2] = np.nan if rawValues[2] == '' else float(rawValues[2])
      rawValues[3] = int(rawValues[3])
      rawValues[4] = int(rawValues[4])
      rawValues[9] = np.nan if rawValues[9] == '' else float(rawValues[9])
      rawValues[11] = np.nan if rawValues[11] == '' else float(rawValues[11])
      rawValues[12] = np.nan if rawValues[12] == '' else float(rawValues[12])
      if rawValues[1] == prevSubject_id:
        for j in (range(len(rawValues[:len(names)]))):
          listsForPandas[j].append(rawValues[j])

      else:
        for j in range(len(names)):
          lab[names[j]] = listsForPandas[j]
          listsForPandas[j] = []
        formNewPatient(lab)
        prevSubject_id = rawValues[1]
        lab = pd.DataFrame(columns=names)
      countLines_ += 1
    except BaseException:
      print('error on', countLines_)
      countLines_ += 1
      prevSubject_id = rawValues[1]

    if countLines_ > 10000:
      break
    if (countLines_ % 1000000 == 0):
      print(countLines_)

print('done')
print('countLines_', countLines_)
print('diagnosFail', diagnosFail)
print('procedureFail', procedureFail)
print('admissionFail', admissionFail)
print('itemsFail', itemsFail)
