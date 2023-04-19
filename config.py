CHAT_LANG = 'Chinese'
# CHAT_LANG = 'English'
max_tokens_per_generation: int = 200
temperature: float = 1.1
top_p: float = 0.8
model_path="./models/Raven3Bv9xctx4096ENCN-Q4.bin"
alpha_presence=0.2
alpha_frequency=0.2