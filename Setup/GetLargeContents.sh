function GetUnzipFile()
{
FUrl=$1
FNm=$2
echo $FUrl
echo $FNm
wget -O download.zip $FUrl
unzip download.zip -d $FNm
rm download.zip
}

GetUnzipFile https://www.dropbox.com/sh/5pty18i8k07ymuu/AADbCv9uypqfA4sqsNV5cmMOa?dl=0 models
GetUnzipFile https://www.dropbox.com/sh/d9f11jiyk042959/AABhH6wP9tPe_xrZnNVj--ZVa?dl=0 pretrained_models
GetUnzipFile https://www.dropbox.com/sh/slz3hf91fl11nww/AACArhUlKtAKOFQ09syFzx7_a?dl=0 MULTI_COMET_DATA
GetUnzipFile https://www.dropbox.com/sh/o0rvxjo12nj2vr4/AABqSGsiYeGB38ITteRrflzfa?dl=0 data
GetUnzipFile https://www.dropbox.com/sh/64kn98wiap9cgau/AAAGDI84XTXaaelhZRzXr7o_a?dl=0 model