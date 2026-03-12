from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date

NORMALIZE_ERROR_CODES = {
    "1": "UNEXPECTED_TYPE",
    "2": "ARGUMENT_MISSING",
    "3": "NULL_VALUES",
    "4": "BAD_VALUE"
}

class InvalidFormatError(ValueError):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

def normalize_list_dict(list_entity, list_name, validation_logic = None, dict_format = None):
    verify_lists(list_entity, list_name)
    normalized = []

    if dict_format is None or not isinstance(dict_format, str):
        raise InvalidFormatError(NORMALIZE_ERROR_CODES["2"], f"dict_format não especificado, deve ser uma str")
        
    for data in list_entity:
        if not isinstance(data, dict):
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], f"Cada item deve ser um objeto { dict_format }")
        
        if not callable(validation_logic):
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["2"], f"Deve haver uma lógica de validação para a função.")
        
        # deve retornar um objeto ex: {"id": 1, "quantity": 2}
        validated = validation_logic(data)
        if validated is None:
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["3"], "A lista de itens não pode estar vazia")
        
        normalized.append(validated)
    return normalized

def verify_lists(list_entity, list_name):
    if list_entity is None:
        raise InvalidFormatError(NORMALIZE_ERROR_CODES["2"], f"O campo '{list_name}' é obrigatório")

    if not isinstance(list_entity, list):
        raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], f"O campo '{list_name}' deve ser uma lista")


def parse_js_date(date_str: str) -> date | None:
    if not date_str or date_str.strip() == "":
        return None

    # Tenta alguns formatos comuns de JS (ISO 8601, apenas data, etc.)
    formats = [
        "%Y-%m-%d",                # só data
        "%Y-%m-%dT%H:%M",          # data + hora sem segundos
        "%Y-%m-%dT%H:%M:%S",       # data + hora com segundos
        "%Y-%m-%dT%H:%M:%S.%fZ",   # ISO com milissegundos e Z
        "%Y-%m-%dT%H:%M:%S%z",     # ISO com timezone
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO com milissegundos + timezone
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Formato de data inválido: {date_str}")


def parse_money(value):
    if isinstance(value, str):
        clean = value.replace("R$", "").replace(",", ".").strip()
    else:
        clean = str(value)

    try:
        dec = Decimal(clean).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return dec
    except Exception:
        raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], "Valor inválido para o campo monetário")
    

def normalize_items(items, field="items"):
    verify_lists(items, field)

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], "Cada item deve ser um objeto {id, quantity}")

        try:
            product_id = int(item.get("id"))
            quantity = int(item.get("quantity"))
        except (ValueError, TypeError):
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], "Campos 'id' e 'quantity' devem ser inteiros")

        if quantity <= 0:
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["4"], "Quantidade deve ser maior que zero")

        normalized.append({"id": product_id, "quantity": quantity})

    if not normalized:
        raise InvalidFormatError(NORMALIZE_ERROR_CODES["3"], "A lista de itens não pode estar vazia")

    return normalized

def new_normalize_items(items):
    def validate_items(item):
        try:
            product_id = int(item.get("id"))
            quantity = int(item.get("quantity"))
        except (ValueError, TypeError):
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], "Campos 'id' e 'quantity' devem ser inteiros")

        if quantity <= 0:
            raise InvalidFormatError(NORMALIZE_ERROR_CODES["4"], "Quantidade deve ser maior que zero")
        
        return {"id": product_id, "quantity": quantity}

    return normalize_list_dict(items, "items", validate_items, "{id, quantity}")

def normalize_payment_method(payment):
    ALLOWED_METHODS = ["pix", "debit", "credit", "cash"]
    def validate_payment_method(row):
            method = row.get("method")
            value = parse_money(row.get("value"))

            if method not in ALLOWED_METHODS:
                raise InvalidFormatError(NORMALIZE_ERROR_CODES["1"], "'method' deve ser um valor dentre: ['pix', 'debit', 'credit', 'cash']")
            
            if value <= -1:
                raise InvalidFormatError(NORMALIZE_ERROR_CODES["4"], "'value' não pode ser um valor negativo")
            
            return {"method": method, "value": value}

    return normalize_list_dict(payment, "payment", validate_payment_method, "{method, value}")
    