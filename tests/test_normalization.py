from app.normalization import normalize_question


def test_normalizes_english_country_and_month_aliases():
    assert normalize_question("How much did we sell in Spain in March?") == "How much did we sell in España in month=03?"


def test_normalizes_spanish_aliases_and_market_phrase():
    assert normalize_question("Ventas del Spanish market en enero") == "Ventas del España en month=01"
