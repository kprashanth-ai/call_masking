from models import Case, CaseStatus, Paramedic
import exotel_client
import session_store


def assign_paramedic(case: Case, paramedic: Paramedic) -> Case:
    if case.status != CaseStatus.open:
        raise ValueError(f"Case {case.id} is not open (status: {case.status})")

    proxy = exotel_client.VIRTUAL_NUMBER
    if not proxy:
        raise RuntimeError("EXOTEL_VIRTUAL_NUMBER not set in .env")

    session_store.set_session(proxy, {
        "case_id": case.id,
        "patient_phone": case.patient_phone,
        "paramedic_phone": paramedic.phone,
    })

    return case.model_copy(update={
        "status": CaseStatus.assigned,
        "paramedic_id": paramedic.id,
        "proxy_number": proxy,
    })


def close_case(case: Case) -> Case:
    if case.proxy_number:
        session_store.delete_session(case.proxy_number)

    return case.model_copy(update={
        "status": CaseStatus.closed,
        "proxy_number": None,
    })


def get_sessions() -> dict:
    return session_store.get_all()
