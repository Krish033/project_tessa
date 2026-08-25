$headers = @{
    'Content-Type' = 'application/json'
}



$todo = [PSCustomObject]@{
    title = 'foo';
    body  = 'bar';
} | ConvertTo-Json   

$response = Invoke-RestMethod `
    -Method POST `
    -Uri "https://jsonplaceholder.typicode.com/posts" `
    -Body $todo `
    -Headers $headers


$response | ConvertTo-Json