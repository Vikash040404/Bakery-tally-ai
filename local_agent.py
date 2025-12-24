import requests
import time
import datetime

# --- CONFIGURATION (IMPORTANT!) ---
# You will update this URL after you deploy to the cloud (e.g., https://bakery-app.onrender.com)
CLOUD_URL = "https://YOUR-APP-NAME.onrender.com" 
TALLY_HOST = "http://localhost:9000"

def generate_tally_xml(bill):
    today = datetime.datetime.now().strftime("%Y%m%d")
    cust = bill['customer']
    # If no customer name, Tally expects "Cash" usually
    ledger_name = cust if cust else "Cash"

    xml = f"""<ENVELOPE>
    <HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER>
    <BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC>
    <REQUESTDATA><TALLYMESSAGE xmlns:UDF="TallyUDF">
     <VOUCHER VCHTYPE="Sales" ACTION="Create" OBJVIEW="Invoice Voucher View">
      <DATE>{today}</DATE>
      <PARTYLEDGERNAME>{ledger_name}</PARTYLEDGERNAME>
      <BASICBUYERNAME>{ledger_name}</BASICBUYERNAME>
      <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
      <PERSISTEDVIEW>Invoice Voucher View</PERSISTEDVIEW>
    """
    
    for item in bill['items']:
        qty = float(item.get('quantity', 1))
        rate = float(item.get('price', 0))
        amount = qty * rate
        xml += f"""
        <ALLINVENTORYENTRIES.LIST>
         <STOCKITEMNAME>{item['name']}</STOCKITEMNAME>
         <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
         <RATE>{rate}/box</RATE>
         <AMOUNT>-{amount}</AMOUNT>
         <ACTUALQTY> {qty} box</ACTUALQTY>
         <BILLEDQTY> {qty} box</BILLEDQTY>
        </ALLINVENTORYENTRIES.LIST>"""
        
    xml += """</VOUCHER></TALLYMESSAGE></REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"""
    return xml

def run_agent():
    print(f"🚀 Connecting to {CLOUD_URL}...")
    while True:
        try:
            # 1. Ask Cloud for bills
            resp = requests.get(f"{CLOUD_URL}/api/get-pending-bills")
            if resp.status_code == 200:
                bills = resp.json().get('bills', [])
                
                for bill in bills:
                    print(f"   🧾 Processing Bill for: {bill['customer']}")
                    xml_data = generate_tally_xml(bill)
                    
                    # 2. Push to Tally
                    try:
                        tally_resp = requests.post(TALLY_HOST, data=xml_data, headers={'Content-Type': 'text/xml'})
                        if "<CREATED>1</CREATED>" in tally_resp.text:
                            print("      ✅ Saved to Tally!")
                            requests.post(f"{CLOUD_URL}/api/mark-complete", json={"bill_id": bill['id']})
                        else:
                            print(f"      ❌ Tally Error. Check Ledger Name '{bill['customer']}' exists?")
                    except:
                        print("      ⚠️ Tally not running on Port 9000?")
            
        except Exception as e:
            print(f"Waiting for internet... ({e})")
        
        time.sleep(5) # Wait 5 seconds

if __name__ == "__main__":
    run_agent()
