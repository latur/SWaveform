<?php
$db = new PDO("sqlite:signal.db");

$req = ['chr1', 3000000, 1300000];
# 10 signals from the 1.3M-3M interval of the 1chr with reference to the sample
$stmt = $db->prepare("SELECT * FROM signal as s 
    LEFT JOIN target AS t ON t.id = s.target_id 
    WHERE s.chr = ? AND s.start < ? AND s.end > ? LIMIT 10");
$stmt->execute($req);

foreach ($stmt->fetchAll(PDO::FETCH_ASSOC) as $item) {
    $coverage = [];
    for ($i = 0; $i < strlen($item['coverage']); $i += 2) {
        # Conversion of BLOB data to integer coverage values:
        $coverage[] = ord($item['coverage'][$i]) * 256 + ord($item['coverage'][$i + 1]);
    }
    $item['coverage'] = $coverage;
    print_r($item);
}