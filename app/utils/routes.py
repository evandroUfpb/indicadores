from flask import render_template, jsonify
import logging
from app.data_apis.bcb import get_selic_data
from app.data_apis.conect_post.conect_post import get_pib_data_from_db
from app.data_apis.conect_post.condect_post_desocupacao import get_desocupacao_data_from_db
from app.data_apis.conect_post.conect_post_ipca import get_ipca_data_from_db
from app.data_apis.conect_post.conect_post_selic import get_selic_data_from_db
from app.data_apis.conect_post.conect_post_cambio import get_cambio_data_from_db
from app.data_apis.conect_post.conect_post_pib_pb import get_pib_pb_data_from_db
from app.data_apis.conect_post.conect_post_sbcpb import get_bcpb_data_from_db
from app.data_apis.conect_post.conect_post_desocupacao_pb import get_desocupacao_pb_data_from_db
from app.data_apis.conect_post.conect_post_divliq_pb import get_divliq_data_from_db




def init_routes(app):
    print("Iniciando rotas...")

    @app.route('/')
    def index():
        print("Rota index acessada")
        logging.info("Acessando rota index")
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/painel_brasil')
    def painel_brasil():
        return render_template('painel_brasil.html')

    @app.route('/painel_paraiba')
    def painel_paraiba():
        return render_template('painel_paraiba.html')

    @app.route('/api/pib_db')
    def pib_db_api():
        try:
            logging.info("Iniciando busca de dados do PIB")
            
            data = get_pib_data_from_db()
            
            if data is None:
                logging.error("Dados do PIB retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados do PIB',
                    'dates': [],
                    'values': [],
                    'label': 'PIB do Brasil',
                    'unit': '%'
                }), 500
            
            logging.info(f"Dados do PIB obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados do PIB: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'PIB do Brasil',
                'unit': '%'
            }), 500

    @app.route('/api/pib_pb')
    def pib_pb_api():
        try:
            logging.info("Iniciando busca de dados do PIB da Paraiba")
            
            data = get_pib_pb_data_from_db()
            
            if data is None:
                logging.error("Dados do PIB da Paraíba retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados do PIB da Paraíba',
                    'dates': [],
                    'values': [],
                    'label': 'PIB da Paraíba',
                    'unit': 'Milhões de Reais'
                }), 500
            
            logging.info(f"Dados do PIB da Paraíba obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados do PIB da Paraíba: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'PIB da Paraíba',
                'unit': 'Milhores de Reais%'
            }), 500


    @app.route('/api/desocupacao')
    def desocupacao_api():
        try:
            logging.info("Iniciando busca de dados da Desocupação")
            
            data = get_desocupacao_data_from_db()
            
            if data is None:
                logging.error("Dados da Desocupação retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados da Desocupação',
                    'dates': [],
                    'values': [],
                    'label': 'Taxa de Desocupação',
                    'unit': '%'
                }), 500
            
            logging.info(f"Dados da Desocupação obtidos: {len(data.get('dates', []))} registros")
            logging.info(f"Primeiras 5 datas: {data['dates'][:5]}")
            logging.info(f"Primeiros 5 valores: {data['values'][:5]}")
            
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados da Desocupação: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'Taxa de Desocupação',
                'unit': '%'
            }), 500



    @app.route('/api/desocupacao_pb')
    def desocupacao_pb_api():
            try:
                logging.info("Iniciando busca de dados da Desocupação PB")
                
                data = get_desocupacao_pb_data_from_db()
                
                if data is None:
                    logging.error("Dados da Desocupação da Paraíba retornaram None")
                    return jsonify({
                        'error': 'Não foi possível obter os dados da Desocupação da Paraíba',
                        'dates': [],
                        'values': [],
                        'label': 'Taxa de Desocupação da Paraíba',
                        'unit': '%'
                    }), 500
                
                logging.info(f"Dados da Desocupação da Paraíba obtidos: {len(data.get('dates', []))} registros")
                logging.info(f"Primeiras 5 datas: {data['dates'][:5]}")
                logging.info(f"Primeiros 5 valores: {data['values'][:5]}")
                
                return jsonify(data)
            except Exception as e:
                logging.error(f"Erro ao buscar dados da Desocupação da Paraíba: {e}", exc_info=True)
                return jsonify({
                    'error': str(e),
                    'dates': [],
                    'values': [],
                    'label': 'Taxa de Desocupação da Paraíba',
                    'unit': '%'
                }), 500    


    @app.route('/api/ipca')
    def ipca_pb():
        try:
            logging.info("Iniciando busca de dados do IPCA")
            
            data = get_ipca_data_from_db()
            
            if data is None:
                logging.error("Dados do IPCA retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados do IPCA',
                    'dates': [],
                    'values': [],
                    'label': 'IPCA do Brasil',
                    'unit': '%'
                }), 500
            
            logging.info(f"Dados do IPCA obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados do IPCA: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'IPCA do Brasil',
                'unit': '%'
            }), 500

    @app.route('/api/selic')
    def selic_api():
        try:
            logging.info("Iniciando busca de dados da SELIC")
            
            data = get_selic_data_from_db()
            
            if data is None:
                logging.error("Dados da SELIC retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados da SELIC',
                    'dates': [],
                    'values': [],
                    'label': 'SELIC',
                    'unit': '%'
                }), 500
            
            logging.info(f"Dados da SELIC obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados da SELIC: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'SELIC',
                'unit': '%'
            }), 500        


    @app.route('/api/cambio')
    def cambio_api():
        try:
            logging.info("Iniciando busca de dados do CAMBIO")
            
            data = get_cambio_data_from_db()
            
            if data is None:
                logging.error("Dados do Cambio retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados da CAMBIO',
                    'dates': [],
                    'values': [],
                    'label': 'CAMBIO',
                    'unit': 'U$/R$'
                }), 500
            
            logging.info(f"Dados do Cambio obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados do Cambio: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'CAMBIO',
                'unit': 'U$/R$'
            }), 500


# Rota para o BCPB
    @app.route('/api/bcpb')
    def bcpb_api():
        try:
            logging.info("Iniciando busca de dados do BCPB")
            
            data = get_bcpb_data_from_db()
            
            if data is None:
                logging.error("Dados do BCPB retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados do BCPB',
                    'dates': [],
                    'values': [],
                    'label': 'BCPB do Brasil',
                    'unit': ''
                }), 500
            
            logging.info(f"Dados do bcpb obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados do bcpb: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'BCPB do Brasil',
                'unit': ''
            }), 500


# Rota para o Dívida Pública DIVPUB
    @app.route('/api/divpub')
    def divpub_api():
        try:
            logging.info("Iniciando busca de dados do DIVPUB")
            
            data = get_divliq_data_from_db()
            
            if data is None:
                logging.error("Dados do DIVPUB retornaram None")
                return jsonify({
                    'error': 'Não foi possível obter os dados do DIVPUB',
                    'dates': [],
                    'values': [],
                    'label': 'Dívida Pública do Governo do Estado da Paraíba',
                    'unit': ''
                }), 500
            
            logging.info(f"Dados do DIVPUB obtidos: {len(data.get('dates', []))} registros")
            return jsonify(data)
        except Exception as e:
            logging.error(f"Erro ao buscar dados do DIVPUB: {e}", exc_info=True)
            return jsonify({
                'error': str(e),
                'dates': [],
                'values': [],
                'label': 'Dívida Pública do Governo do Estado da Paraíba',
                'unit': ''
            }), 500            