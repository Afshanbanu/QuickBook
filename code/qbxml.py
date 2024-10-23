from lxml import etree
def buildRequest(requestID=1,iteratorID=""):
    req="""
    <?qbxml version="6.0"?>
    <QBXML>
       <QBXMLMsgsRq onError="stopOnError">
          <AccountQueryRq requestID="1">
           <AccountType>Expense</AccountType>
           <AccountType>Equity</AccountType>
           <AccountType>AccountsPayable</AccountType>
           <AccountType>CreditCard</AccountType>
           <AccountType>OtherCurrentLiability</AccountType>
           <AccountType>LongTermLiability</AccountType>
           <AccountType>OtherExpense</AccountType>
           <AccountType>Bank</AccountType>
           <AccountType>Income</AccountType>
           <AccountType>OtherIncome</AccountType>
           <AccountType>AccountsReceivable</AccountType>
           <AccountType>OtherCurrentAsset</AccountType>
           <AccountType>FixedAsset</AccountType>
           <AccountType>CostOfGoodsSold</AccountType>
          </AccountQueryRq>
          <CustomerQueryRq requestID="2">
          </CustomerQueryRq>
          <EmployeeQueryRq requestID="3">
          </EmployeeQueryRq>
          <ItemQueryRq requestID="4">
          </ItemQueryRq>
       </QBXMLMsgsRq>
    </QBXML>
    """
    return req

