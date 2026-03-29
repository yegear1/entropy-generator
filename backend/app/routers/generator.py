from fastapi import APIRouter, Query, HTTPException

from app.services.entropy_generator import generate_password, generate_passphrase

router = APIRouter(prefix="/api/v1/generate", tags=["Generator"])


@router.get("/password")
async def get_generated_password(
    length: int = Query(24, gt=8, le=128, description="Comprimento da senha (9-128)"),
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_specials: bool = True,
    use_emojis: bool = Query(False, description="Incluir emojis balanceados (pode falhar em alguns sites)")
):
    """
    Gera uma senha aleatória balanceada com alta entropia.
    """
    try:
        senha = generate_password(
            length,
            use_upper=use_upper,
            use_lower=use_lower,
            use_digits=use_digits,
            use_specials=use_specials,
            use_emojis=use_emojis
        )
        return {"password": senha}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar senha: {str(e)}")


@router.get("/passphrase")
async def get_generated_passphrase(
    words: int = Query(6, gt=4, le=32, description="Quantidade de palavras (5-32)"),
    language: str = Query("pt", pattern="^(en|pt)$")
):
    """
    Gera uma passphrase (frase-senha) baseada na wordlist Diceware da EFF.
    """
    try:
        frase = generate_passphrase(words, language=language)
        return {"passphrase": frase}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar passphrase: {str(e)}")