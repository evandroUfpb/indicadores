// Função utilitária para formatar labels
function formatChartLabels(dates, formatType = 'default') {
    console.log('Formatando labels:', dates, formatType);
    console.log('Primeiro elemento das datas:', dates[0]);
    console.log('Último elemento das datas:', dates[dates.length - 1]);

    // Função para extrair ano de uma data
    const extractYear = (dateStr) => {
        const dateObj = new Date(dateStr);
        const year = dateStr.split('-')[0];
        // const year = dateObj.getFullYear();
        console.log(`Extraindo ano de ${dateStr}: ${year}`);
        return year.toString();
    };

    // Mapear datas para anos reais
    const yearLabels = dates.map(extractYear);

    console.log('Anos extraídos:', yearLabels);
    console.log('Número de datas:', dates.length);
    console.log('Número de anos:', yearLabels.length);

    // Adicionar log para verificar a origem dos anos
    console.log('Origem dos anos:', yearLabels.map((year, index) => `${year} (de ${dates[index]})`));

    switch(formatType) {
        case 'yearOnly':
            // Retornar apenas os anos dos dados reais
            return yearLabels;
        
        case 'trimester':
            // Lógica para formatação de trimestres
            return dates.map(date => {
                const dateObj = new Date(date);
                const year = dateObj.getFullYear();
                const month = dateObj.getMonth() + 1;
                const quarter = Math.ceil(month / 3);
                return `${year} T${quarter}`;
            });
        
        default:
            return dates;
    }
}


// Função compartilhada para buscar dados do PIB e montar o gráfico full
function fetchPIBData(chartId = 'pibChartFull', endpoint = '/api/pib_db') {
    //#console.log(`Iniciando busca de dados do PIB no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta do PIB:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados do PIB recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de PIB encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados do PIB disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Usar formatação de trimestre para PIB Brasil
            

            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do PIB');
                return;
            }

        
            const formattedLabels = formatChartLabels(data.dates, 'trimester');



            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.pibChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'PIB',
                        data: data.values,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: Variação Trimestral do PIB'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados do PIB:', error);
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados do PIB: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}


// Função compartilhada para buscar dados do PIB da Paraíba e montar o gráfico full

function fetchPIBPBData(chartId = 'pibPBChartFull', endpoint = '/api/pib_pb') {
    console.log(`Iniciando busca de dados do PIB da Paraíba no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta do PIB da Paraiba:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados do PIB da Paraiba recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de PIB da Paraiba encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados do PIB da Paraiba disponíveis';
                return;
            }

            // Log detalhado dos dados recebidos
            console.log('Datas recebidas:', data.dates);
            console.log('Primeiro elemento das datas:', data.dates[0]);
            console.log('Último elemento das datas:', data.dates[data.dates.length - 1]);


            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do PIB da Paraiba');
                return;
            }

            const formattedLabels = formatChartLabels(data.dates, 'yearOnly');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.pibChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'PIB',
                        data: data.values,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Paraíba: PIB a preços correntes'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados do PIB:', error);
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados do PIB: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}


 // Função compartilhada para buscar dados de Desocupação para montar o gráfico full
 function fetchDesocupacaoData(chartId = 'desocupacaoChartFull', endpoint = '/api/desocupacao') {
    console.log(`Iniciando busca de dados de Desocupação no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para Desocupacao:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de Desocupacao recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de Desocupacao encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados de Desocupacao disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico de Desocupacao' );
                return;
            }

            
            const formattedLabels = formatChartLabels(data.dates, 'trimester');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.desocupacaoChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'Desocupação',
                        data: data.values,
                        borderColor: 'rgb(70, 130, 180)',
                        backgroundColor: 'rgb(70, 130, 180, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: Taxa de Desocupação Trimestral'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados de Desocupacao');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados de Desocupacao: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}


// Função compartilhada para buscar dados de Desocupação da Paraiba para montar o gráfico full
function fetchDesocupacaoPbData(chartId = 'desocupacaoPbChartFull', endpoint = '/api/desocupacao_pb') {
    console.log(`Iniciando busca de dados de Desocupação no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para Desocupacao da Paraíba:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de Desocupação da Paraíba recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de Desocupação da Paraíba encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados de Desocupação da Paraíba disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico de Desocupacao' );
                return;
            }

            
            const formattedLabels = formatChartLabels(data.dates, 'trimester');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.desocupacaoChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'Desocupação',
                        data: data.values,
                        borderColor: 'rgb(70, 130, 180)',
                        backgroundColor: 'rgb(70, 130, 180, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: Taxa de Desocupação Trimestral'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados de Desocupacao');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados de Desocupacao: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}
















// Função compartilhada para buscar dados do IPCA para montar o gráfico full
function fetchIpcaData(chartId = 'IpcaChartFull', endpoint = '/api/ipca') {
    console.log(`Iniciando busca de dados do IPCA no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para ipca:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de ipca recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de ipca encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados de ipca disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do ipca' );
                return;
            }

            // // Converter datas para formato mais legível
            // const formattedLabels = data.dates.map(date => {
            //     // Assumindo que as datas estão no formato YYYY-MM-DD ou YYYY
            //     const dateObj = new Date(date);
            //     return dateObj.getFullYear().toString();
            // });

            const formattedLabels = formatChartLabels(data.dates, 'monthly');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.ipcaChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'IPCA',
                        data: data.values,
                        borderColor: 'rgb(135,206,250)',
                        backgroundColor: 'rgba(135,206,250, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: IPCA - Mensal'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados de Desocupacao');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados de Desocupacao: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}


// Função compartilhada para buscar dados da SELEC para montar o gráfico full

function fetchSelicData(chartId = 'SelicChartFull', endpoint = '/api/selic') {
    console.log(`Iniciando busca de dados da SELEC no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para Selic:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de Selic recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado da Selic encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados da Selic disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico da Selic' );
                return;
            }

            // // Converter datas para formato mais legível
            // const formattedLabels = data.dates.map(date => {
            //     // Assumindo que as datas estão no formato YYYY-MM-DD ou YYYY
            //     const dateObj = new Date(date);
            //     return dateObj.getFullYear().toString();
            // });

            const formattedLabels = formatChartLabels(data.dates, 'monthly');


            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.selicChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'SELIC',
                        data: data.values,
                        borderColor: 'rgb(135,206,250)',
                        backgroundColor: 'rgba(135,206,250, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: Taxa Selic - Mensal'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados da Selic');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados da Selic: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}


// Função compartilhada para buscar dados do CAMBIO para montar o gráfico full

function fetchCambioData(chartId = 'CambioChartFull', endpoint = '/api/cambio') {
    console.log(`Iniciando busca de dados do CAMBIO no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para o Cambio:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de Selic recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado do Cambio encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados do Cambio disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do Cambio' );
                return;
            }

            // // Converter datas para formato mais legível
            // const formattedLabels = data.dates.map(date => {
            //     // Assumindo que as datas estão no formato YYYY-MM-DD ou YYYY
            //     const dateObj = new Date(date);
            //     return dateObj.getFullYear().toString();
            // });

            const formattedLabels = formatChartLabels(data.dates, 'daily');



            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.CambioChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'CAMBIO',
                        data: data.values,
                        borderColor: 'rgb(135,206,250)',
                        backgroundColor: 'rgba(135,206,250, 0.2)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: Taxa de Câmbio (Últimos 30 dias)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'U$/R$' //data.unit
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados do Câmbio');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados do Cambio: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}


// Função compartilhada para buscar dados do BCPB para montar o gráfico full

function fetchBcpbData(chartId = 'BcpbChartFull', endpoint = '/api/bcpb') {
    console.log(`Iniciando busca de dados do BCPB no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para bcpb:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de bcpb recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de bcpb encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados de bcpb disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do bcpb' );
                return;
            }

            // // Converter datas para formato mais legível
            // const formattedLabels = data.dates.map(date => {
            //     // Assumindo que as datas estão no formato YYYY-MM-DD ou YYYY
            //     const dateObj = new Date(date);
            //     return dateObj.getFullYear().toString();
            // });

            const formattedLabels = formatChartLabels(data.dates, 'monthly');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);


             // Criar datasets com cores condicionais
             const datasets = [{
                label: 'BCPB',
                data: data.values,
                borderWidth: 2,
                tension: 0.1,
                // Usar uma função para definir a cor baseada no valor
                borderColor: data.values.map(value => value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)'),
                backgroundColor: data.values.map(value => value >= 0 ? 'rgba(135,206,250, 0.2)' : 'rgba(255,0,0, 0.2)'),
                segment: {
                    borderColor: ctx => {
                        const value = ctx.p0DataIndex !== undefined ? data.values[ctx.p0DataIndex] : 0;
                        return value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)';
                    }
                }
            }];

            window.ipcaChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: datasets
                    // data: {
                    //     labels: formattedLabels,
                    //     datasets: datasets
                    },
                    // datasets: [{
                    //     label: 'BCPB',
                    //     data: data.values,
                    //     borderColor: 'rgb(135,206,250)',
                    //     backgroundColor: 'rgba(135,206,250, 0.2)',
                    //     borderWidth: 2,
                    //     tension: 0.1
                    //}]
                
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Paraíba: Saldo da Balança Comercial'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || 'Valor'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Erro completo ao buscar dados de BCPB');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados de BCPB: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}

