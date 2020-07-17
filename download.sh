mkdir -p ./staticb/db && \
apt-get update && \
apt-get install -y wget && \
wget -O ./staticb/db/wn-multi.db "https://www.dropbox.com/s/zo4u1lbvjuajm8a/wn-multi.db?dl=1" && \
wget -O ./staticb/db/wnall.db "https://www.dropbox.com/s/3vszhzz4eafeoqo/wnall.db?dl=1" && \
wget -O ./staticb/wn-ocal.zip "https://www.dropbox.com/s/mz3r9vn0obpo3tt/wn-ocal.zip?dl=1"
