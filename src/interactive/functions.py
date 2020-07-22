import torch

from src.data.utils import TextEncoder
import src.data.config as cfg
import src.data.data as data
import src.models.models as models
from src.evaluate.sampler import BeamSampler, GreedySampler, TopKSampler

import utils.utils as utils

#adrian added
import os

def load_model_file(model_file):
    model_stuff = data.load_checkpoint(model_file)
    opt = model_stuff["opt"]
    state_dict = model_stuff["state_dict"]

    return opt, state_dict

def load_data(dataset, opt, LoaderPath=""):
    if dataset == "atomic":
        data_loader = load_atomic_data(opt, LoaderPath)
    elif dataset == "conceptnet":
        data_loader = load_conceptnet_data(opt)

    # Initialize TextEncoder
    encoder_path = "model/encoder_bpe_40000.json"
    bpe_path = "model/vocab_40000.bpe"
    text_encoder = TextEncoder(encoder_path, bpe_path)
    #print(text_encoder.encoder)##DEBUG
    #print('\n\n\n\n\n\n')#DEBUG
    #print(text_encoder.encoder)#DEBUG
    text_encoder.encoder = data_loader.vocab_encoder
    text_encoder.decoder = data_loader.vocab_decoder
    #print('SLOVENE')#DEBUG
    #print('\n\n\n\n\n\n')#DEBUG
    #print(text_encoder.encoder)#DEBUG
    #print('to sam ya')

    return data_loader, text_encoder


def load_atomic_data(opt, LoaderPath=""):
    # Hacky workaround, you may have to change this
    # if your models use different pad lengths for e1, e2, r
    ###################SET MAXE1, MAXE2 HERE ASWELL
    ###############################################################################
    #print(opt)#DEBUG
    if opt.data.get("maxe1", None) is None:
        opt.data.maxe1 = 50 ###DEFAULT FOR COMET PRETRAINED MODELS: MAXE1=17 , MAXE2 = 35 MAXR=1
        opt.data.maxe2 = 35
        opt.data.maxr = 1

    path = "data/atomic/processed/generation/{}.pickle".format(
        utils.make_name_string(opt.data))
    #data loader is made directly from data in atomic folder
    data_loader = data.make_data_loader(opt, opt.data.categories)
    #loaded = data_loader.load_data(path)###OLD####
    #ADRIAN ADDED##############################CHANGE FOR DIFF LOADER
    if(LoaderPath ==""):
      print('No loader path provided, using defalut loader');
      loaded = data_loader.load_data(path)###OLD####
    else:
      print("Loader Path Provided:", LoaderPath)
      #FPathEng = 'MULTI_COMET_DATA/It50k_MaxE50/English/Eng_Loader_It50k_maxE50.pickle'
      #FPathSlo = 'MULTI_COMET_DATA/It50k_MaxE50/Slovene/Slo_Loader_It50k_maxE50.pickle'
      print("IS VALID FILE: ", os.path.isfile(LoaderPath))
      loaded = data_loader.load_data(LoaderPath)
    ##########################
    #print(data_loader.vocab_encoder)#DEBUG

    return data_loader


def load_conceptnet_data(opt):
    # Hacky workaround, you may have to change this
    # if your models use different pad lengths for r
    if opt.data.get("maxr", None) is None:
        if opt.data.rel == "language":
            opt.data.maxr = 5
        else:
            opt.data.maxr = 1
    path = "../data/conceptnet/processed/generation/{}.pickle".format(
    utils.make_name_string(opt.data))
    data_loader = data.make_data_loader(opt)
    loaded = data_loader.load_data(path)
    return data_loader


def make_model(opt, n_vocab, n_ctx, state_dict):
    model = models.make_model(
        opt, n_vocab, n_ctx, None, load=False,
        return_acts=True, return_probs=False)

    models.load_state_dict(model, state_dict)

    model.eval()
    return model


def set_sampler(opt, sampling_algorithm, data_loader):
    if "beam" in sampling_algorithm:
        opt.eval.bs = int(sampling_algorithm.split("-")[1])
        sampler = BeamSampler(opt, data_loader)
    elif "topk" in sampling_algorithm:
        # print("Still bugs in the topk sampler. Use beam or greedy instead")
        # raise NotImplementedError
        opt.eval.k = int(sampling_algorithm.split("-")[1])
        sampler = TopKSampler(opt, data_loader)
    else:
        sampler = GreedySampler(opt, data_loader)

    return sampler


def get_atomic_sequence(input_event, model, sampler, data_loader, text_encoder, category, EventN):
    if isinstance(category, list):
        outputs = {}
        for cat in category:
            new_outputs = get_atomic_sequence(
                input_event, model, sampler, data_loader, text_encoder, cat)
            outputs.update(new_outputs)
        return outputs
    #MUST SELECT ALL FOR JSON FILE WRITE TO WORK
    elif category == "all":
        ######ADRIAN ADDED
        #####SAVING COMET TAGS TO JSON
         #ADDED
        with open('COMETTags.json', 'a', -1, "utf8") as f:
            f.write("  {\n")
            f.write("    \"EventId\" : " + str(EventN) + ',\n')
            f.write("    \"EventStr\" : \"")
            for ChN in range(len(input_event)):#go character by character to change special characters to json syntax ex.  "
                if (input_event[ChN] == '"'):
                    f.write("\\\"")#add \" instead of " to file to keep Json format
                elif (input_event[ChN] == '/'):
                    f.write("\\/")
                elif (input_event[ChN] == '\\'):
                    f.write("\\\\")
                elif (input_event[ChN] == '\t'):
                    f.write("\\t")
                elif (input_event[ChN] == '\b'):
                    f.write("\\b")
                elif (input_event[ChN] == '\f'):
                    f.write("\\f")
                elif (input_event[ChN] == '\n'):
                    f.write("\\n")
                elif (input_event[ChN] == '\r'):
                    f.write("\\r")
                elif (input_event[ChN] == '\t'):
                    f.write("\\t")
                else:
                    f.write(input_event[ChN])
            ##########################
            f.write("\",\n")
        outputs = {}

        #########ADRIAN ADDED
        first=True
        ##################
        for category in data_loader.categories:
            ######ADRIAN ADDED
            if first:
                first = False
            else:
                with open('COMETTags.json', 'a') as f:
                    f.write(',')
            ##################
            new_outputs = get_atomic_sequence(
                input_event, model, sampler, data_loader, text_encoder, category, EventN)
            outputs.update(new_outputs)
        #ADRIAN ADDED
        with open('COMETTags.json', 'a') as f:
            f.write("  }\n")
        ##################
        return outputs
    else:

        sequence_all = {}

        sequence_all["event"] = input_event
        sequence_all["effect_type"] = category

        with torch.no_grad():

            batch = set_atomic_inputs(
                input_event, category, data_loader, text_encoder)

            sampling_result = sampler.generate_sequence(
                batch, model, data_loader, data_loader.max_event +
                data.atomic_data.num_delimiter_tokens["category"],
                data_loader.max_effect -
                data.atomic_data.num_delimiter_tokens["category"])

        sequence_all['beams'] = sampling_result["beams"]

        
       #ORIGINAL PRINT MODEL RESULTS
        #print_atomic_sequence(sequence_all)
        ########ADRIAN ADDED 
        #ADRIAN ADDED###############################################
        write_atomic_sequence_beam(sequence_all)
        #######################################################
        return {category: sequence_all}

#ADRIAN ADDED#########################
def write_atomic_sequence_beam(sequence_object):
  input_event = sequence_object["event"]
  category = sequence_object["effect_type"]

  with open('COMETTags.json', 'a') as f:

    f.write("    \"" + category + "\" : [\n")
    first = True
    for beam in sequence_object["beams"]:
        if first:
            first = False
        else:
            f.write(", ")
        f.write('"')
        for ChN in range(len(beam)):
            if (beam[ChN] == '"'):
                f.write("\\\"")#add \" instead of " to file to keep Json format
            elif (beam[ChN] == '/'):
                f.write("\\/")
            elif (beam[ChN] == '\\'):
                f.write("\\\\")
            elif (beam[ChN] == '\t'):
                f.write("\\t")
            elif (beam[ChN] == '\b'):
                f.write("\\b")
            elif (beam[ChN] == '\f'):
                f.write("\\f")
            elif (beam[ChN] == '\n'):
                f.write("\\n")
            elif (beam[ChN] == '\r'):
                f.write("\\r")
            elif (beam[ChN] == '\t'):
                f.write("\\t")
            else:
                f.write(beam[ChN])
        f.write('"')
    f.write("\n      ]\n")
#########################################################

def print_atomic_sequence(sequence_object):
    input_event = sequence_object["event"]
    category = sequence_object["effect_type"]

    print("Input Event:   {}".format(input_event))
    print("Target Effect: {}".format(category))
    print("")
    print("Candidate Sequences:")
    for beam in sequence_object["beams"]:
        print(beam)
    print("")
    print("====================================================")
    print("")


def set_atomic_inputs(input_event, category, data_loader, text_encoder):
    XMB = torch.zeros(1, data_loader.max_event + 1).long().to(cfg.device)
    prefix, suffix = data.atomic_data.do_example(text_encoder, input_event, None, True, None)

    XMB[:, :len(prefix)] = torch.LongTensor(prefix)
    XMB[:, -1] = torch.LongTensor([text_encoder.encoder["<{}>".format(category)]])

    batch = {}
    batch["sequences"] = XMB
    batch["attention_mask"] = data.atomic_data.make_attention_mask(XMB)

    return batch


def get_conceptnet_sequence(e1, model, sampler, data_loader, text_encoder, relation, force=False):
    if isinstance(relation, list):
        outputs = {}

        for rel in relation:
            new_outputs = get_conceptnet_sequence(
                e1, model, sampler, data_loader, text_encoder, rel)
            outputs.update(new_outputs)
        return outputs
    elif relation == "all":
        outputs = {}

        for relation in data.conceptnet_data.conceptnet_relations:
            new_outputs = get_conceptnet_sequence(
                e1, model, sampler, data_loader, text_encoder, relation)
            outputs.update(new_outputs)
        return outputs
    else:

        sequence_all = {}

        sequence_all["e1"] = e1
        sequence_all["relation"] = relation

        with torch.no_grad():
            if data_loader.max_r != 1:
                relation_sequence = data.conceptnet_data.split_into_words[relation]
            else:
                relation_sequence = "<{}>".format(relation)

            batch, abort = set_conceptnet_inputs(
                e1, relation_sequence, text_encoder,
                data_loader.max_e1, data_loader.max_r, force)

            if abort:
                return {relation: sequence_all}

            sampling_result = sampler.generate_sequence(
                batch, model, data_loader,
                data_loader.max_e1 + data_loader.max_r,
                data_loader.max_e2)

        sequence_all['beams'] = sampling_result["beams"]

        print_conceptnet_sequence(sequence_all)

        return {relation: sequence_all}


def set_conceptnet_inputs(input_event, relation, text_encoder, max_e1, max_r, force):
    abort = False

    e1_tokens, rel_tokens, _ = data.conceptnet_data.do_example(text_encoder, input_event, relation, None)

    if len(e1_tokens) >  max_e1:
        if force:
            XMB = torch.zeros(1, len(e1_tokens) + max_r).long().to(cfg.device)
        else:
            XMB = torch.zeros(1, max_e1 + max_r).long().to(cfg.device)
            return {}, True
    else:
        XMB = torch.zeros(1, max_e1 + max_r).long().to(cfg.device)

    XMB[:, :len(e1_tokens)] = torch.LongTensor(e1_tokens)
    XMB[:, max_e1:max_e1 + len(rel_tokens)] = torch.LongTensor(rel_tokens)

    batch = {}
    batch["sequences"] = XMB
    batch["attention_mask"] = data.conceptnet_data.make_attention_mask(XMB)

    return batch, abort


def print_conceptnet_sequence(sequence_object):
    e1 = sequence_object["e1"]
    relation = sequence_object["relation"]

    print("Input Entity:    {}".format(e1))
    print("Target Relation: {}".format(relation))
    print("")
    print("Candidate Sequences:")
    for beam in sequence_object["beams"]:
        print(beam)
    print("")
    print("====================================================")
    print("")


def print_help(data):
    print("")
    if data == "atomic":
        print("Provide a seed event such as \"PersonX goes to the mall\"")
        print("Don't include names, instead replacing them with PersonX, PersonY, etc.")
        print("The event should always have PersonX included")
    if data == "conceptnet":
        print("Provide a seed entity such as \"go to the mall\"")
        print("Because the model was trained on lemmatized entities,")
        print("it works best if the input entities are also lemmatized")
    print("")


def print_relation_help(data):
    print_category_help(data)


def print_category_help(data):
    print("")
    if data == "atomic":
        print("Enter a possible effect type from the following effect types:")
        print("all - compute the output for all effect types {{oEffect, oReact, oWant, xAttr, xEffect, xIntent, xNeed, xReact, xWant}}")
        print("oEffect - generate the effect of the event on participants other than PersonX")
        print("oReact - generate the reactions of participants other than PersonX to the event")
        print("oEffect - generate what participants other than PersonX may want after the event")
    elif data == "conceptnet":
        print("Enter a possible relation from the following list:")
        print("")
        print('AtLocation')
        print('CapableOf')
        print('Causes')
        print('CausesDesire')
        print('CreatedBy')
        print('DefinedAs')
        print('DesireOf')
        print('Desires')
        print('HasA')
        print('HasFirstSubevent')
        print('HasLastSubevent')
        print('HasPainCharacter')
        print('HasPainIntensity')
        print('HasPrerequisite')
        print('HasProperty')
        print('HasSubevent')
        print('InheritsFrom')
        print('InstanceOf')
        print('IsA')
        print('LocatedNear')
        print('LocationOfAction')
        print('MadeOf')
        print('MotivatedByGoal')
        print('NotCapableOf')
        print('NotDesires')
        print('NotHasA')
        print('NotHasProperty')
        print('NotIsA')
        print('NotMadeOf')
        print('PartOf')
        print('ReceivesAction')
        print('RelatedTo')
        print('SymbolOf')
        print('UsedFor')
        print("")
        print("NOTE: Capitalization is important")
    else:
        raise
    print("")

def print_sampling_help():
    print("")
    print("Provide a sampling algorithm to produce the sequence with from the following:")
    print("")
    print("greedy")
    print("beam-# where # is the beam size")
    print("topk-# where # is k")
    print("")
