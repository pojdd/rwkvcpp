# Provides terminal-based chat interface for RWKV model.

import os
import sys
import argparse
import pathlib
import sampling
import tokenizers
import rwkv_cpp_model
import rwkv_cpp_shared_library
import copy

with open("config.py", 'rb') as file:
    CHAT_LANG = None
    max_tokens_per_generation = None
    temperature = None
    top_p = None
    model_path = None
    exec(compile(file.read(), "config.py", 'exec'))
    
PROMPT_FILE = f'./prompt/default/{CHAT_LANG}-2.py'

with open(PROMPT_FILE, 'rb') as file:
    user = None
    bot = None
    interface = None
    init_prompt = None
    exec(compile(file.read(), PROMPT_FILE, 'exec'))
init_prompt = init_prompt.strip().split('\n')
for c in range(len(init_prompt)):
    init_prompt[c] = init_prompt[c].strip().strip('\u3000').strip('\r')
init_prompt = '\n' + ('\n'.join(init_prompt)).strip() + '\n\n'
bot_message_prefix: str = bot+interface
user_message_prefix: str = user+interface

assert init_prompt != '', 'Prompt must not be empty'

# print('Loading 20B tokenizer')
tokenizer = tokenizers.Tokenizer.from_file('20B_tokenizer.json')

library = rwkv_cpp_shared_library.load_rwkv_shared_library()
# print(f'System info: {library.rwkv_get_system_info_string()}')
print('加载模型...')
model = rwkv_cpp_model.RWKVModel(library, model_path)
init_prompt=""
prompt_tokens = tokenizer.encode(init_prompt).ids
prompt_token_count = len(prompt_tokens)
# print(f'处理 {prompt_token_count}个 prompt tokens, 等待中...')

logits, state = None, None

for token in prompt_tokens:
    logits, state = model.eval(token, state, state, logits)
    
print("使用+reset 重置对话")
print('初始化成功，请输入。')
print("\n> "+user_message_prefix,end=' ',flush=True)
stateInit=copy.deepcopy(state)
logitsInit=copy.deepcopy(logits)
user_input=""

while True:
    # Read user input
    user_input = sys.stdin.readline()
    if user_input[:6] == "+reset":
        state=copy.deepcopy(stateInit)
        logits=copy.deepcopy(logitsInit)
        print("> "+user_message_prefix,end=' ',flush=True)
        continue
    # Process the input
    new_tokens = tokenizer.encode(user_input.strip()).ids

    for token in new_tokens:
        logits, state = model.eval(token, state, state, logits)

    # Generate and print bot response
    print("> "+bot_message_prefix,end='',flush=True)
    END_OF_TEXT = 100257
    END_OF_LINE = 198

    decoded = ''
    all_tokens = []
    out_last = 0
    occurrence = {}
    send_msg=""
    
    alpha_presence=0.2
    alpha_frequency=0.2
    
    occurrence = {}
    for i in range(max_tokens_per_generation):
        for n in occurrence:
            logits[n] -= (alpha_presence + occurrence[n] * alpha_frequency)
            
        token = sampling.sample_logits(logits, temperature, top_p)
        all_tokens += [token]
        if token not in occurrence:
            occurrence[token] = 1
        else:
            occurrence[token] += 1
        
        decoded = tokenizer.decode(all_tokens[out_last:])
        
        if '\ufffd' not in decoded:
            print(decoded, end='', flush=True)
            send_msg+=decoded
            out_last = i + 1
            
        logits, state = model.eval(token, state, state, logits)
        
        # 对话结束
        # if '\n\n' == send_msg[-2:]:
        #     send_msg = send_msg.strip()
        #     break
        
        # 生成结束
        if token == END_OF_TEXT:
            break
    if '\n' not in decoded:
        print()
    print("> "+user_message_prefix,end=' ',flush=True)
