import sqlite3

class SQLController:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
    
    ##QUERYING USER
    def GetUserType(self, username,password):
        self.cursor.execute('SELECT utype FROM users WHERE uid=:username AND pwd=:password',{"username":username,"password":password})
        user = self.cursor.fetchone()
        self.connection.commit()
        if user is None: 
            return None
        else:
            uType=user[0]
            return uType    
        
    def QueryUserCity(self, username):
        self.cursor.execute('SELECT city FROM users WHERE uid=:username',{"username":username})
        city = self.cursor.fetchone()
        if city is None:
            return None
        else: 
            return city[0]
        
    ##QUERYING BIRTHS   
    def CheckUniqueBirthRegno(self, regno):
        self.cursor.execute('SELECT * FROM births WHERE regno=:regno',{"regno":regno})
        result = self.cursor.fetchone()
        if result is None:
            #if nothing found, the regno is unique and does not exist yet
            return False
        else:
            return True
    
    def CreateBirth(self, regno, fname, lname, regdate, regplace, gender, ffname, flname, mfname, mlname):
        try:
            self.cursor.execute('INSERT INTO births VALUES(:regno ,:fname ,:lname ,:regdate ,:regplace ,:gender,:ffname,:flname,:mfname,:mlname)',{"regno":regno, "fname":fname, "lname":lname, "regdate":regdate, "regplace":regplace, "gender":gender, "ffname":ffname, "flname":flname, "mfname":mfname, "mlname":mlname})
            self.cursor.commmit()
        except:
            return True

    ##QUERYING PERSONS
    def QueryPersonsAll(self, first, last):
        self.cursor.execute('SELECT * FROM persons WHERE fname=:first AND lname=:last',{"first":first, "last":last})
        person = self.cursor.fetchone()
        if person is None:
            return None
        else:
            return person
        
    def CreatePerson(self, fname, lname, bdate, bplace, address, phone):
        try:
            self.cursor.execute('INSERT INTO persons VALUES(:fname ,:lname ,:bdate ,:bplace ,:address ,:phone)',{"fname":fname, "lname":lname, "bdate":bdate, "bplace":bplace, "address":address, "phone":phone})
            self.connection.commit()
        except:
            return True
    ##QUERY TICKETS
    def GetTicketFine(self, ticketnum):
        self.cursor.execute('SELECT fine FROM tickets WHERE tno=:ticketnum',{'ticketnum':ticketnum})
        fine = self.cursor.fetchone()
        return int(fine[0])    
    
    ##QUERY PAYMENTS
    def GetAllPayments(self, ticketnum):
        self.cursor.execute('SELECT amount FROM payments WHERE tno=:ticketnum',{'ticketnum':ticketnum})
        payments = self.cursor.fetchall()
        return payments
        
    def ProcessPayment(self, ticketnum, ticketdate, ticketamount):
        try:
            self.cursor.execute('INSERT INTO payments VALUES(:ticketnum, :ticketdate, :ticketamount)',{'ticketnum':ticketnum, 'ticketdate':ticketdate, 'ticketamount':ticketamount})
            self.connection.commit()
        except:
            #Return True if error happened in sql execution
            #sqlite3 module in python cannot return specific error, can only say some error happened and make guess on cause. 
            return True
        
    ##TRAFFIC OFFICER##
    ##ISSUE TICKET APP
    def GetReg(self, rn):
        self.cursor.execute('SELECT fname, lname, make, model, year, color FROM registrations r, vehicles v WHERE r.vin = v.vin AND regno=:number',{"number":rn})
        reg = self.cursor.fetchone()  
        self.connection.commit()
        if reg is None:
            return None
        else:
            return reg 
        
    def CheckUniqueTicketNo(self, tno):
        self.cursor.execute('SELECT * FROM tickets WHERE tno=:tno',{"tno":tno})
        result = self.cursor.fetchone()
        self.connection.commit()
        if result is None:
            return False
        else:
            return True 
        
    def CreateTicket(self, tno, regno, fine, violation, vdate):
        self.cursor.execute('INSERT INTO tickets VALUES(:tno ,:regno ,:fine ,:violation ,:vdate)',{"tno":tno, "regno":regno, "fine":fine, "violation":violation, "vdate":vdate})
        self.connection.commit()    
    
    ##FIND CAR OWNER
    def FindCarOwner(self,make,model,year,color,plate):
        criteriaLst=[]
        if len(make)!=0:
            criteriaLst.append('make LIKE '+"'%"+str(make)+"%'")
        if len(model)!=0:
            criteriaLst.append('model LIKE '+"'%"+str(model)+"%'")
        if len(year)!=0:
            criteriaLst.append('year LIKE '+"'%"+str(year)+"%'")
        if len(color)!=0:
            criteriaLst.append('color LIKE '+"'%"+str(color)+"%'")
        if len(plate)!=0:
            criteriaLst.append('plate LIKE '+"'%"+str(plate)+"%'")
        criteriaStr = ' AND '.join(criteriaLst)
        
        self.cursor.execute('SELECT make, model, year, color, plate, MAX(regdate), expiry, fname, lname FROM registrations r, vehicles v WHERE r.vin=v.vin AND ' + criteriaStr + ' GROUP BY r.vin')
        result = self.cursor.fetchall()
        self.connection.commit()
        if result is None:
            return False
        else:
            return result
    
    def Abstract(self,fname,lname):
        self.cursor.execute('select count(t1.tno), count(d1.ddate), sum(d1.points),count(t2.tno), count(d2.ddate), sum(d2.points) from tickets t1, tickets t2, registrations r1, registrations r2, demeritNotices d1, demeritNotices d2 where d1.fname = :fname and d1.lname = :lname and r1.fname = :fname and r1.lname = :lname and r1.regno = t1.regno and d2.fname = :fname and d2.lname = :lname and r2.fname = :fname and r2.lname = :lname and r2.regno = t2.regno and t2.vdate > date("now", "-2 years") and d2.ddate > date("now", "-2 years")',{"fname":fname,"lname":lname})
        return self.cursor.fetchall()
    
    def TicketView(self,fname,lname):
        self.cursor.execute('select tno, vdate, violation, fine, t.regno, make, model from tickets t, registrations r, vehicles v where r.regno = t.regno and r.vin = v.vin and r.fname = :fname and r.lname = :lname order by vdate desc',{"fname":fname,"lname":lname})
        return self.cursor.fetchall()
    
    def MarriageReg(self,regno,regdate,regplace,fname1,lname1,fname2,lname2):
        self.cursor.execute('INSERT INTO marriages VALUES(:regno,:regdate,:regplace,:fname1,:lname1,:fname2,:lname2',{'regno':regno,'regdate':regdate,'regplace':regplace,'fname1':fname1,'lname1':lname1,'fname2':fname2,'lanem2':lname2})
        self.connection.commit()
    
    def CheckUniqueMarriageRegno(self,regno):
        self.cursor.execute('SELECT * FROM marriages WHERE regno=:regno',{"regno":regno})
        result = self.cursor.fetchone()
        if result is None:
            #if nothing found, the regno is unique and does not exist yet
            return False
        else:
            return True

    def CommitAndClose(self):
        self.connection.commit()	
        self.connection.close()
