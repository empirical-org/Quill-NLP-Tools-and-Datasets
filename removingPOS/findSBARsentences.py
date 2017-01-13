#Now need to find sentences for the subordinate clause category (SBAR)
import re

def subordinate_removal(s):
    regCap = re.compile(r'(After|Although|As|Because|Before|If|Once|Since|Than|That|Though|Unless|Until|When|Whenever|Where|Whereas|'
                       'Wherever|Whether|While|Why|Even if|Even though|Provided that|Rather than|So that|In order that)(?=\s)'
                       )
    regLow = re.compile(r'(?<=\s)(after|although|as|because|before|if|once|since|than|that|though|unless|until|when|whenever|where|whereas|'
                       'wherever|whether|while|why|even if|even though|provided that|rather than|so that|in order that)(?=\s)'
                       )
    check_Cap_found = regCap.search(s)
    if check_Cap_found != None: # in this match we know starts at zero, just look for first comma index
        first_comma_index = s.find(',')
        if first_comma_index > -1:
            return (s[:first_comma_index] + '.', check_Cap_found.group())
        else:
            return ('COMMA ERROR',None)
    else:
        check_Low_found = regLow.search(s)
        if check_Low_found != None: # we know the span will be greater than zero so go till end
            sub_start_index = check_Low_found.span()[0]
            short_sub_sent = s[sub_start_index:]
            upd_short_sent = short_sub_sent[0].upper() + short_sub_sent[1:]
            return (upd_short_sent.rstrip('\n'),check_Low_found.group())
    return ("ERROR",None) # here return an error message as string


with open('./updatedSentences/errorSentences.txt','w') as error:
    with open('./updatedSentences/subordinateCompleteSentences.txt','w') as complete:
        with open('./updatedSentences/subordinateRemovedSentences.txt','w') as remov:
            with open('./originalSentences/subordinateConjunctionSentences.txt','r') as file:
                for line in file:
                    updated_sent = subordinate_removal(line)
                    if updated_sent[0] != 'ERROR' and updated_sent[0] != 'COMMA ERROR':
                        complete.write(line)
                        remov.write(updated_sent[0] + ' ||| ' + updated_sent[1] + ' ||| ' + line)
                    else:
                        error.write(line)
