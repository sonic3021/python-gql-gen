# -*- coding: utf-8 -*-

"""Main module."""

import pathlib
import json
import click
import sys
from functools import reduce
from pprint import PrettyPrinter
from graphql.utils.base  import introspection_query,  build_client_schema
from graphql.utils.schema_printer import print_schema
from graphql.utils.build_ast_schema import build_ast_schema
from graphql.language.base import Source , parse
from graphqlclient import GraphQLClient



def args_to_vars_str(obj):
    _avs=''
    if obj.keys():
        _avs=', '.join(list(map(lambda kv: '{}: ${}'.format(kv[0],kv[0]) , obj.items())))
    return _avs

def vars_to_types_str(obj):
    _vts=''
    if obj.keys():
        _vts=', '.join(list(map(lambda kv: '${}: {}'.format(kv[0],kv[1].type) , obj.items())))
    return _vts


def get_field_arg_dict(field,duplicate_c,all_args={}):
    _arg_dict=dict()
    for _arg in field.args:

        if _arg in duplicate_c:
            index=duplicate_c[_arg]+1
            duplicate_c[_arg]=index
            _arg_dict[_arg+str(index)]=field.args[_arg]
        elif _arg in all_args:
            duplicate_c[_arg]=1
            _arg_dict[_arg+'1']=field.args[_arg]
        else:
            _arg_dict[_arg]=field.args[_arg]
    return _arg_dict



def gen_query(schema, cur_name, cur_p_type=None,cur_p_name=None, arg_dict={},duplicate_c={},cross_ref_key_l=[],cur_depth=1 ):
    query=''
    field=schema.get_type(str(cur_p_type)).fields[cur_name]
    ct=field.type
    ctname=ct.name
    child_query=''
    sub_query_l=[]

    if hasattr(ct,'fields'):
        for key in ct.fields:
            sub_field=ct.fields[key]
            sub_query_tmp=gen_query(schema, key ,ct,cur_name,arg_dict,duplicate_c, cross_ref_key_l, cur_depth+1)[0]
            sub_query_l.append(sub_query_tmp)
        child_query='\n'.join(sub_query_l)

    if not (hasattr(ct,'fields') and not child_query):
        query='    '*cur_depth+cur_name

        if field.args:
           f_arg_dict=get_field_arg_dict(field,duplicate_c,arg_dict)
           arg_dict=f_arg_dict
           query+='('+args_to_vars_str(f_arg_dict)+')'

        if child_query:
            query+='{{\n{}\n{}}} '.format(child_query, '    '*cur_depth)



    return query ,arg_dict
    # TODO  the union type
    # if ct.astNode and ct.astNode.kind== 'UnionTypeDefinition':
    #     union_query=''
    #     types=ct.types
    #     if types and types.length:
    #         indent= ' '*cur_depth
    #         frag=' '* cur_depth+1
    #         query+='{\n'

    #         for i in range(0, types.length  ):
    #             value_type_name=types[i]
    #             value_type=schema.gettype(value_type_name)
    #             for key in value_type.fields:
    #                 _tmp_q=gen_query(cur,value_type,cur_name,arg_dict,duplicate_c ,cross_ref_key_l, cur_depth+2)
    #                 union_query+=_tmp_q
    #             query+="{}... on {} {{\n {}\n {} }}\n"
    #         query+=indent




def get_schema(url, directory=None):
    pp = PrettyPrinter(indent=4)
    client = GraphQLClient(url)
    intros_result = client.execute(introspection_query, variables=None)
    dict_res=json.loads(intros_result)
    client_schema = build_client_schema(dict_res['data'])
    sdl = print_schema(client_schema)
    if directory:
        path=pathlib.Path(directory)
        if not path.is_absolute():

            path=pathlib.Path(path.cwd(),path)

        file_path=pathlib.Path(path,"graphql.schema")
        print(file_path)
        with open(file_path, 'w+') as f :
            f.write(sdl)
    else:
        print(sdl)
    return sdl


def parse_schema_to_gql(schema_str=None,directory=None):
    gqls=Source(schema_str)
    gqld=parse(gqls)
    schema=build_ast_schema(gqld)
    q_tpl='{} {}{} {{\n{}\n}}'

    if directory:
        path=pathlib.Path(directory)
        if not path.is_absolute():
            path=pathlib.Path(path.cwd(),path)

        pathlib.Path( path, 'query').mkdir(parents=True, exist_ok=True)
        pathlib.Path( path, 'mutation').mkdir( parents=True, exist_ok=True)
        pathlib.Path( path, 'subscription').mkdir( parents=True, exist_ok=True)



    print(path)
    if schema.get_query_type():
        for field in schema.get_query_type().fields:
            qstr, arg_dict=gen_query(schema , field,'Query')
            vars_types_str=vars_to_types_str(arg_dict)
            if vars_types_str:
                vars_types_str='({})'.format(vars_types_str)
            q_str=q_tpl.format('query',field, vars_types_str, qstr)

            if directory:
                file_path=pathlib.Path(path,'query',"{}.graphql".format(field))
                print(file_path)
                with open(file_path, 'w+') as f :
                    f.write(q_str)
            else:
                print(q_str)
#    if schema.get_query_type():
#        for field in schema.get_query_type().fields:
#            qstr, arg_dict=gen_query(schema , field,'Query')
#            vars_types_str=vars_to_types_str(arg_dict)
    #         if vars_types_str:
    #             vars_types_str='({})'.format(vars_types_str)
    #         print(q_tpl.format('query',field, vars_types_str, qstr))
    # if schema.get_query_type():
    #     for field in schema.get_query_type().fields:
    #         qstr, arg_dict=gen_query(schema , field,'Query')
    #         vars_types_str=vars_to_types_str(arg_dict)
    #         if vars_types_str:
    #             vars_types_str='({})'.format(vars_types_str)
    #         print(q_tpl.format('query',field, vars_types_str, qstr))
