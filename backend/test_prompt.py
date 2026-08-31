import os
import sys

sys.path.append(os.path.join("c:\\Users\\amna.malik\\Desktop\\vanna\\VannaAI\\backend"))

from app.services.vanna_service import get_vanna, _POP_INSTANCE_KEY

try:
    vn = get_vanna(_POP_INSTANCE_KEY)
    prompt = vn.get_sql_prompt(
        question="How many invoices are not verified?",
        question_sql_list=[],
        ddl_list=[],
        doc_list=[],
        schema_constraint="CPPA_NOT_VERIFIED_ALERT_T: INVOICE_NO (varchar), INV_TYPE (varchar)"
    )
    print("PROMPT TYPE:", type(prompt))
    if isinstance(prompt, list):
        for idx, msg in enumerate(prompt):
            print(f"--- MSG {idx} ({msg.get('role')}) ---")
            print(msg.get('content')[:500] + "..." if len(msg.get('content', '')) > 500 else msg.get('content'))
    else:
        print(prompt)
except Exception as e:
    print("Error:", e)
