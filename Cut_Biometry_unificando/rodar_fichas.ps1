$base = "C:/Users/rj0369870548/Desktop/Projects_VsCode/Corte_fichas/Cut_Biometry/Cut_Biometry_unificando"
$lista = Get-Content "$base\arquivos_fichas\imagens_jpg.txt"
foreach ($nome in $lista) {
    $imagem = "$base\arquivos_fichas\$nome"
    $saida = "$base\saida\$($nome -replace '.jpg','')"
    python "$base\unify_pipeline.py" $imagem --output $saida
}
