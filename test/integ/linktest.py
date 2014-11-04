##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
import requests
import config
import unittest
import helper
import json
import logging

class LinkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LinkTest, self).__init__(*args, **kwargs)
        self.endpoint = 'http://' + config.get('server') + ':' + str(config.get('port'))
       
    def testGet(self):
        logging.info("LinkTest.testGet")
        for domain_name in ('tall', 'tall_ro'):
            g1_uuid = None
            domain = domain_name + '.' + config.get('domain')   
            rootUUID = helper.getRootUUID(domain)     
            req = self.endpoint + "/groups/" + rootUUID + "/links/g1"
            headers = {'host': domain}
            rsp = requests.get(req, headers=headers)
            self.failUnlessEqual(rsp.status_code, 200)
            rspJson = json.loads(rsp.text)
            target = rspJson['target']
            self.assertTrue(target.startswith("/groups/"))
            self.assertTrue("created" in rspJson)
            self.assertTrue("lastModified" in rspJson)
            self.failUnlessEqual(rspJson['class'], 'hard')
            self.failUnlessEqual(rspJson['name'], 'g1')
                            
    def testGetBatch(self):
        logging.info("MemberTest.testGetBatch")
        domain = 'group1k.' + config.get('domain')   
        rootUUID = helper.getRootUUID(domain)     
        req = helper.getEndpoint() + "/groups/" + rootUUID + "/links"
        headers = {'host': domain}
        params = {'Limit': 50 }
        names = set()
        # get links in 20 batches of 50 links each
        lastName = None
        for batchno in range(20):
            if lastName:
                params['Marker'] = lastName
            rsp = requests.get(req, headers=headers, params=params)
            self.failUnlessEqual(rsp.status_code, 200)
            if rsp.status_code != 200:
                break
            rspJson = json.loads(rsp.text)
            links = rspJson['links']
            self.failUnlessEqual(len(links) <= 50, True)
            for link in links:
                lastName = link['name']
                names.add(lastName)
            if len(links) == 0:
                break
        self.failUnlessEqual(len(names), 1000)  # should get 1000 unique links
        
    def testGetBadParam(self):
        logging.info("LinkTest.testGetBatchBadParam")
        domain = 'tall.' + config.get('domain')   
        rootUUID = helper.getRootUUID(domain)     
        req = helper.getEndpoint() + "/groups/" + rootUUID + "/links"
        headers = {'host': domain}
        params = {'Limit': 'abc' }
        rsp = requests.get(req, headers=headers, params=params)
        self.failUnlessEqual(rsp.status_code, 400)
    
        
    def testPut(self):
        logging.info("MemberTest.testPut")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'g3'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)  # link doesn't exist
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)  # it's there now!
        # make a request second time (verify idempotent)
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testPutNameWithSpaces(self):
        logging.info("LinkTest.testPutNameWithSpaces")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'name with spaces'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testPutBadReqId(self):
        logging.info("LinkTest.testPutBadReqId")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        badReqId  = 'b2771194-347f-11e4-bb67-3c15c2da029e' # doesn't exist in tall.h5
        name = 'g3'
        req = helper.getEndpoint() + "/groups/" + badReqId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testPutBadLinkId(self):
        logging.info("LinkTest.testPutBadLinkId")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)  
        badLinkId  = 'b2771194-347f-11e4-bb67-3c15c2da029e' # doesn't exist in tall.h5
        name = 'g3'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": badLinkId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        
    def testPutNoName(self):
        logging.info("LinkTest.testPutNoName")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/"  
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testPutBadName(self):
        logging.info("LinkTest.testPutBadName")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'bad/name'  # forward slash not allowed
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 400)
        
    def testPutSoftLink(self):
        logging.info("LinkTest.testPutSoftLink")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'softlink'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"h5path": "/somewhere"}
        headers = {'host': domain}
        # verify softlink does not exist
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 404)
        # make request
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        # verify link is created
        rsp = requests.get(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        # verify idempotent
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
    def testDelete(self):
        logging.info("LinkTest.testDelete")
        domain = 'tall_updated.' + config.get('domain') 
        grpId = helper.createGroup(domain)
        rootId = helper.getRootUUID(domain)   
        name = 'deleteme'
        req = helper.getEndpoint() + "/groups/" + rootId + "/links/" + name 
        payload = {"id": grpId}
        headers = {'host': domain}
        rsp = requests.put(req, data=json.dumps(payload), headers=headers)
        self.failUnlessEqual(rsp.status_code, 201)
        
        # now remove the link
        rsp = requests.delete(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
        # get should fail
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 410)
        
        # Group should still be accessible via uuid
        req = self.endpoint + "/groups/" + grpId
        rsp = requests.get(req, headers=headers)
        self.failUnlessEqual(rsp.status_code, 200)
        
    
       
if __name__ == '__main__':
    unittest.main()