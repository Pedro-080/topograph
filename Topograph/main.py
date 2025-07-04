import os
import sys

def encontrar_arquivos_txt(pasta_executavel):
    """Encontra todos os arquivos .txt na pasta do executável"""
    arquivos_txt = []
    for item in os.listdir(pasta_executavel):
        if item.lower().endswith('.txt') and os.path.isfile(os.path.join(pasta_executavel, item)):
            # Ignora arquivos que já são resultados de processamento
            if not ('_CAD' in item or '_QGIS' in item):
                arquivos_txt.append(os.path.join(pasta_executavel, item))
    return arquivos_txt

def processar_arquivo(caminho_arquivo):
    """Processa o arquivo aplicando ajuste de Z se necessário"""
    linhas_tratadas = []
    ajuste_z = 0.0
    primeira_linha_especial = False
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        # Verifica a primeira linha para ajuste de Z
        primeira_linha = f.readline().strip()
        
        if primeira_linha.startswith('Z+=') or primeira_linha.startswith('Z-='):
            primeira_linha_especial = True
            try:
                ajuste_z = float(primeira_linha[3:])
                if primeira_linha.startswith('Z-='):
                    ajuste_z = -ajuste_z
            except ValueError:
                print(f"[AVISO] Valor de ajuste Z inválido: {primeira_linha}")
        
        # Se a primeira linha era especial, continuamos a leitura
        # Se não era, precisamos processar essa linha
        if not primeira_linha_especial:
            f.seek(0)  # Volta ao início do arquivo
        
        for num_linha, linha in enumerate(f, 1 if primeira_linha_especial else 1):
            linha = linha.strip()
            if not linha:
                continue
                
            valores = linha.split(',')
            if len(valores) < 2:
                print(f"[AVISO] Linha {num_linha} com formato inválido: {linha}")
                continue
                
            primeiro_valor = valores[0]
            
            # Verifica se o primeiro valor NÃO é um número inteiro
            if not primeiro_valor.isdigit():
                # Concatena o primeiro valor ao último (com espaço)
                valores[-1] = f"{valores[-1]} {primeiro_valor}"
            
            # Aplica ajuste Z se houver (assumindo que Z é o 4º valor, índice 3)
            if len(valores) >= 4 and ajuste_z != 0.0:
                try:
                    z = float(valores[3])
                    z_ajustado = z + ajuste_z
                    valores[3] = f"{z_ajustado:.3f}"  # Formata para 3 casas decimais
                except ValueError:
                    print(f"[AVISO] Valor Z inválido na linha {num_linha}: {valores[3]}")
            
            # Substitui o primeiro valor pelo número da linha (em todos os casos)
            valores[0] = str(num_linha)
            linhas_tratadas.append(','.join(valores))
    
    return linhas_tratadas

def salvar_arquivos_tratados(caminho_original, linhas_tratadas):
    """Salva duas versões do arquivo tratado: _CAD e _QGIS"""
    diretorio, nome_arquivo = os.path.split(caminho_original)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    
    # Caminhos para os novos arquivos
    caminho_CAD = os.path.join(diretorio, f"{nome_base}_CAD{extensao}")
    caminho_QGIS = os.path.join(diretorio, f"{nome_base}_QGIS{extensao}")
    
    # Cabeçalho para o arquivo QGIS
    cabecalho = "ITEM,COORD_Y,COORD_X,COORD_Z,Descrição"
    
    # Salva versão CAD (sem cabeçalho)
    with open(caminho_CAD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas_tratadas))
    
    # Salva versão QGIS (com cabeçalho)
    with open(caminho_QGIS, 'w', encoding='utf-8') as f:
        f.write(cabecalho + '\n')
        f.write('\n'.join(linhas_tratadas))
    
    return caminho_CAD, caminho_QGIS

def main():
    print("=== PROCESSADOR AUTOMÁTICO DE DADOS TOPOGRÁFICOS ===")
    
    # Obtém o diretório onde o executável está localizado
    pasta_executavel = os.path.dirname(sys.argv[0])
    
    print(f"\nProcurando arquivos .txt em: {pasta_executavel}")
    arquivos = encontrar_arquivos_txt(pasta_executavel)
    
    if not arquivos:
        print("Nenhum arquivo .txt encontrado para processamento.")
        os.system("pause")
        return
    
    print("\nArquivos encontrados:")
    for i, arquivo in enumerate(arquivos, 1):
        print(f"{i}. {os.path.basename(arquivo)}")
    
    for arquivo in arquivos:
        print(f"\nProcessando: {os.path.basename(arquivo)}...")
        
        try:
            linhas_tratadas = processar_arquivo(arquivo)
            cad_path, qgis_path = salvar_arquivos_tratados(arquivo, linhas_tratadas)
            
            print(f"Arquivos gerados:")
            print(f"- {os.path.basename(cad_path)} (formato CAD)")
            print(f"- {os.path.basename(qgis_path)} (formato QGIS)")
            print(f"Total de pontos processados: {len(linhas_tratadas)}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao processar {os.path.basename(arquivo)}: {str(e)}")
    
    print("\n=== PROCESSAMENTO CONCLUÍDO ===")
    os.system("pause")

if __name__ == "__main__":
    main()