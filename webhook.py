import os
from flask import Flask, request, Response
import session_store
import exotel_client

app = Flask(__name__)


def normalize(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    return digits[-10:] if len(digits) >= 10 else digits


def exoml(target: str, caller_id: str) -> Response:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial callerId="{caller_id}" record="true" action="/webhook/status">
        <Number>{target}</Number>
    </Dial>
</Response>"""
    return Response(xml, mimetype="text/xml")


def reject() -> Response:
    return Response(
        '<?xml version="1.0"?><Response><Reject/></Response>',
        mimetype="text/xml"
    )


@app.route("/webhook/inbound", methods=["POST"])
def inbound_call():
    caller = request.form.get("From", "")
    dialed = request.form.get("To", "")
    call_sid = request.form.get("CallSid", "")

    print(f"[inbound] CallSid={call_sid}  From={caller}  To={dialed}")

    session = session_store.get_session(dialed)
    if not session:
        print(f"[inbound] No active session for {dialed}")
        return reject()

    caller_norm = normalize(caller)
    patient_norm = normalize(session["patient_phone"])
    paramedic_norm = normalize(session["paramedic_phone"])

    if caller_norm == patient_norm:
        target = session["paramedic_phone"]
        print(f"[inbound] Patient → routing to MCO {target}")
    elif caller_norm == paramedic_norm:
        target = session["patient_phone"]
        print(f"[inbound] MCO → routing to patient {target}")
    else:
        print(f"[inbound] Unknown caller {caller} — rejecting")
        return reject()

    return exoml(target=target, caller_id=exotel_client.VIRTUAL_NUMBER)


@app.route("/webhook/status", methods=["POST"])
def call_status():
    data = dict(request.form)
    print(f"[status] {data}")
    return Response("OK", status=200)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
