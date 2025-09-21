from typing import Optional

from pydantic import BaseModel


class CreateInvoiceResponse(BaseModel):
    id: str
    url: str


class _GetInvoiceStatusResponseCancel(BaseModel):
    status: str
    """
        processing - заявление на отмену находится в обработке
        success - заявление на отмену выполнено успешно
        failure - неуспешная отмена
    """

    amount: int
    ccy: int

    created_date: str
    modified_date: str

    approval_code: str
    transaction_id: str
    operation_reference: str


class GetInvoiceStatusResponse(BaseModel):
    id: str

    status: str
    """
        created - счет создан успешно, ожидается оплата
        processing - платеж обрабатывается
        hold - сумма заблокирована
        success - успешная оплата
        failure - неуспешная оплата
        reversed - оплата возвращена после успеха
        expired - время действия исчерпано
    """

    failure_reason: str
    error_code: str

    amount: int
    ccy: int
    final_amount: int

    created_date: str
    modified_date: str

    reference: str
    destination: str

    cancel: Optional[_GetInvoiceStatusResponseCancel] = None
