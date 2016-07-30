import logging
import time
import csv
from googleads import adwords

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)


def checkCampaignReport(client):
    # Initialize appropriate service.
    report_downloader = client.GetReportDownloader(version='v201605')
    
    # Create report query
    report_query = ('SELECT CampaignId, AccountDescriptiveName '
                  'FROM CAMPAIGN_PERFORMANCE_REPORT '
                  'WHERE TrackingUrlTemplate CONTAINS "{lpurl}" '
                  'DURING TODAY')
    
    return report_downloader.DownloadReportAsStringWithAwql(
      report_query, 'CSV', skip_report_header=False, skip_column_header=False,
      skip_report_summary=True, include_zero_impressions= True)


def checkKeywordReport(client):
    # Initialize appropriate service.
    report_downloader = client.GetReportDownloader(version='v201605')
    
    # Create report query, using exact match to identify correct TrackingUrlTemplate first, later missing paras will be checked
    report_query = ('SELECT AccountDescriptiveName, Criteria, TrackingUrlTemplate '
                  'FROM KEYWORDS_PERFORMANCE_REPORT '
                  'WHERE TrackingUrlTemplate != "{lpurl}&mk={keyword}&ad={matchtype}&crtv={creative}&psite=mkwid|{_mkwid}&device={device}" '    
                  'DURING TODAY')
    
    return report_downloader.DownloadReportAsStringWithAwql(
      report_query, 'CSV', skip_report_header=False, skip_column_header=False,
      skip_report_summary=True, include_zero_impressions= True)



if __name__ == '__main__':
    # CSV paths
    PathCam = "./Campaign_report_download.csv"
    PathKey = "./Keyword_report_download.csv"
    # four adwords customer accounts ID
    idList = ['182-364-1249','499-751-1439', '244-940-6544', '539-287-0046']

    # Keyword Template parameters list
    paraList = ['{lpurl}','mk={keyword}', 'ad={matchtype}', 'crtv={creative}', 'psite=mkwid|{_mkwid}', 'device={device}']

    # Initialize client object
    adwords_client = adwords.AdWordsClient.LoadFromStorage()

    # recording Campaigns containing TrackingUrlTemplate
    resultCam = checkCampaignReport(adwords_client)

    with open(PathCam,'wb') as fileCam:
        wrCam = csv.writer(fileCam)
        # write report header and column header
        wrCam.writerow(resultCam.splitlines()[0].split('"'))
        wrCam.writerow(['CampaignId', 'AccountDescriptiveName'])

        for i in range(len(idList)):
            adwords_client.SetClientCustomerId(idList[i])
            resultCam = checkCampaignReport(adwords_client)
            # if the query result contains more than 2 lines, then alerting it contains TrackingUrlTemplate
            if len(resultCam.splitlines()) > 2:
                print "%s, Campaign %s has TrackingURLTemplate!"%(resultCam.splitlines()[2].split(',')[1], 
                                                                  resultCam.splitlines()[2].split(',')[0])
            for i in range(2,len(resultCam.splitlines())):
                wrCam.writerow(resultCam.splitlines()[i].split(','))


    #recording Keyword without TrackingUrlTemplate or with missing paras
    resultKey = checkKeywordReport(adwords_client)

    with open(PathKey,'wb') as fileKey:
        wrKey = csv.writer(fileKey)
    
        # write report header and column header
        wrKey.writerow(resultKey.splitlines()[0].split('"'))
        wrKey.writerow(['AccountDescriptiveName', 'Criteria', 'missingPara'])

        for i in range(len(idList)):
            adwords_client.SetClientCustomerId(idList[i])
            resultKey = checkKeywordReport(adwords_client)
            for i in range(2,len(resultKey.splitlines())):
                comparaList = resultKey.splitlines()[i].split(',')[2].split('&')
                # compare parameter list with tracking template to find missing paras
                if set(paraList) < set(comparaList):
                    print "%s , Keyword %s, no missing parameters, but containing extra para: %s"%(resultKey.splitlines()[i].split(',')[0], 
                                                                                                  resultKey.splitlines()[i].split(',')[1],
                                                                                                  set(comparaList) - set(paraList))
                else:
                    missingList = list(set(paraList) - set(comparaList))
                    if (comparaList[0].strip() == '--') & (len(comparaList) == 1):
                        print "%s , Keyword %s has no TrackingURLTemplate"%(resultKey.splitlines()[i].split(',')[0], 
                                                                           resultKey.splitlines()[i].split(',')[1])
                    else:
                        print "%s , Keyword %s has missing paras %s"%(resultKey.splitlines()[i].split(',')[0], 
                                                                      resultKey.splitlines()[i].split(',')[1],
                                                                 missingList)
                    line =resultKey.splitlines()[i].split(',')[:2] + missingList
                    wrKey.writerow(line)
   