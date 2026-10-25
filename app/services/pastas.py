import re

from fastapi import HTTPException

from app.services.cloudinary import listar_subpastas, normalizar_nome_empresa


def consultar_pasta_empresa(conn, id_empresa: int) -> dict:
    with conn.cursor() as cursor:
        cursor.execute('SELECT nome FROM public.empresa WHERE id = %s', (id_empresa,))
        empresa = cursor.fetchone()

        if empresa is None:
            raise HTTPException(404, 'Empresa não encontrada')

        prefixo = f'{normalizar_nome_empresa(empresa[0])}-'
        for pasta in listar_subpastas('acta-arquivos'):
            if not pasta.startswith(prefixo):
                continue

            for subpasta in listar_subpastas(f'acta-arquivos/{pasta}'):
                ciclo = re.fullmatch(r'ciclo-([0-9]+)', subpasta)
                if ciclo is None:
                    continue

                cursor.execute(
                    'SELECT 1 FROM pdca.ciclo WHERE id = %s AND id_empresa = %s',
                    (int(ciclo.group(1)), id_empresa)
                )
                if cursor.fetchone() is not None:
                    return {'pasta': pasta}

    raise HTTPException(404, 'Pasta da empresa não encontrada')