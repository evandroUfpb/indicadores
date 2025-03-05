function formatChartLabels(dates, formatType = 'trimester') {
    console.log('Formatando labels:', dates, formatType);

    switch(formatType) {
        case 'yearOnly':
            return dates.map(date => date.substring(0, 4));
        
        case 'trimester':
            return dates.map(date => {
                const year = date.substring(0, 4);
                const month = parseInt(date.substring(5, 7), 10);
                const quarter = Math.ceil(month / 3);
                
                const formattedLabel = `${year} T${quarter}`;
                console.log(`🕰️ Data original: ${date}, Label formatado: ${formattedLabel}`);
                return formattedLabel;
            });
        
        case 'monthly':
            return dates.map(date => {
                const year = date.substring(0, 4);
                const month = parseInt(date.substring(5, 7), 10);
                
                // Array de nomes de meses abreviados
                const monthNames = [
                    'Jan', 'Fev', 'Mar', 'Abr', 
                    'Mai', 'Jun', 'Jul', 'Ago', 
                    'Set', 'Out', 'Nov', 'Dez'
                ];
                
                // Formatar como "Ano - Mês" a cada 6 meses
                return `${year} - ${monthNames[month - 1]}`;
            });
        
        default:
            return dates;
    }
}



// Função compartilhada para buscar dados do PIB e montar o gráfico full
function fetchPIBData() {
    console.log('🚀 Iniciando fetchPIBData()');
    
    const ctx = document.getElementById('pibChartFull');
    
    if (!ctx) {
        console.error('❌ Elemento do gráfico PIB não encontrado');
        console.log('🔍 Elementos disponíveis:', document.getElementsByTagName('canvas'));
        return;
    }

    console.log('✅ Elemento do canvas encontrado:', ctx);

    fetch('/api/pib_db')
        .then(response => {
            console.log('✅ Resposta recebida da API de PIB');
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Dados do PIB recebidos:', data);
            
            // Log detalhado dos dados
            console.log('🕰️ Datas originais:', data.dates);
            console.log('📈 Valores:', data.values);
            
            // Verificar se há dados suficientes
            if (!data.dates || !data.values || data.dates.length === 0) {
                console.error('❌ Dados insuficientes para renderizar o gráfico');
                return;
            }

            const formattedLabels = formatChartLabels(data.dates, 'trimester');
            console.log('🏷️ Labels formatados:', formattedLabels);

            
            // Destruir gráfico existente, se houver
            if (window.pibChart instanceof Chart) {
                console.log('🗑️ Destruindo gráfico PIB existente');
                window.pibChart.destroy();
            }

            const ctxChart = ctx.getContext('2d');
            console.log('🖼️ Contexto do canvas obtido:', ctxChart);


            const datasets = [{
                label: 'PIBBR',
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


            window.pibChart = new Chart(ctxChart, {
                type: 'bar',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'PIB (%)',
                        borderWidth: 2,
                        tension: 0.1,
                        data: data.values,
                        borderColor: data.values.map(value => value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)'),
                        backgroundColor: data.values.map(value => value >= 0 ? 'rgba(135,206,250, 0.2)' : 'rgba(255,0,0, 0.2)'),
                        segment: {
                            borderColor: ctx => {
                                const value = ctx.p0DataIndex !== undefined ? data.values[ctx.p0DataIndex] : 0;
                                return value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)';
                                }
                        }
                        
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
                        x: {
                            title: {
                                display: false,
                                text: 'Trimestres'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '(%)'
                            }
                        }
                    }
                }
            });

            console.log('✅ Gráfico PIB renderizado com sucesso');
        })
        .catch(error => {
            console.error('❌ Erro completo ao buscar dados do PIB:', error);
            const chartElement = document.getElementById('pibChartFull');
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

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do PIB da Paraiba');
                return;
            }

            // Log detalhado dos dados recebidos
            console.log('Datas recebidas:', data.dates);
            console.log('Primeiro elemento das datas:', data.dates[0]);
            console.log('Último elemento das datas:', data.dates[data.dates.length - 1]);


            const formattedLabels = formatChartLabels(data.dates, 'yearOnly');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', data.values);

            window.pibChart = new Chart(ctx, {
                type: 'bar',
                
                data: {
                    labels: data.dates.map(date => {
                        // Extrai diretamente os primeiros 4 caracteres (ano)
                        const year = date.substring(0, 4);
                        console.log(`🕰️ Data original: ${date}, Ano extraído: ${year}`);
                        return year;
                    }),
                    

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
  function fetchDesocupacaoData(chartId = 'desocupacaoChartFull', endpoint = '/api/desocupacao', dynamicRange = true) {
    console.log(`🔍 Iniciando busca de dados no endpoint: ${endpoint}`);
    
    const chartElement = document.getElementById(chartId);
    if (!chartElement) {
        console.error(`❌ Elemento do gráfico com ID '${chartId}' não encontrado`);
        return;
    }

    fetch(endpoint)
        .then(response => {
            console.log('📡 Resposta recebida:', response);
            if (!response.ok) {
                throw new Error(`Erro HTTP! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('🔍 Dados recebidos:', data);
            console.log('📅 Datas originais:', data.dates);
            console.log('📊 Valores originais:', data.values);

            if (!data.dates || !data.values || data.dates.length === 0) {
                console.error('❌ Sem dados disponíveis');
                chartElement.innerHTML = 'Sem dados disponíveis';
                return;
            }

            const ctx = chartElement.getContext('2d');
            

            // Lógica para intervalo dinâmico 

            let filteredDates = data.dates;
            let filteredValues = data.values;

            if (dynamicRange) {
                // Encontrar a data mais recente
                const lastDate = new Date(Math.max(...data.dates.map(date => new Date(date))));
                
                // Calcular data 10 anos atrás
                const tenYearsAgo = new Date(lastDate.getFullYear() - 10, lastDate.getMonth(), lastDate.getDate());
                
                // Filtrar dados
                const filteredData = data.dates.reduce((acc, date, index) => {
                    const currentDate = new Date(date);
                    if (currentDate >= tenYearsAgo) {
                        acc.dates.push(date);
                        acc.values.push(data.values[index]);
                    }
                    return acc;
                }, { dates: [], values: [] });

                filteredDates = filteredData.dates;
                filteredValues = filteredData.values;

                console.log(`🕰️ Dados filtrados de ${tenYearsAgo.toISOString().split('T')[0]} a ${lastDate.toISOString().split('T')[0]}`);
            }

            const formattedLabels = formatChartLabels(filteredDates, 'yearMonth');

            // // Destruir gráfico existente
            // if (window.desocupacaoChart instanceof Chart) {
            //     window.desocupacaoChart.destroy();
            // }

            window.desocupacaoChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    //labels: data.dates,
                    datasets: [{
                        label: 'Taxa de Desocupação',
                        //data: data.values,
                        data: filteredValues,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Brasil: Taxa de Desocupação'  
                        },
                    },
                    scales: {
                        x: {
                            title: {
                             display: true
                                
                            }
                        },
                        y: {
                            min: 2,
                            max: 17,
                            ticks: {
                                stepSize: 2
                                        },
                            title: {
                                display: true,
                                text: '(%)'
                            }
                        }
                    }
                }
            });

            console.log('✅ Gráfico renderizado com sucesso');
        })
        .catch(error => {
            console.error('❌ Erro completo ao buscar dados:', error);
            chartElement.innerHTML = `Erro ao carregar dados: ${error.message}`;
        });
}



function fetchDesocupacaoPbData(chartId = 'desocupacaoPbChartFull', endpoint = '/api/desocupacao_pb', dynamicRange = true   ) {
    console.log(`Iniciando busca de dados de Desocupação da Paraíba no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de Desocupação da Paraíba encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados de Desocupação da Paraíba disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico de Desocupação da Paraíba');
                return;
            }

            // Lógica para intervalo dinâmico
            let filteredDates = data.dates;
            let filteredValues = data.values;

            if (dynamicRange) {
                // Encontrar a data mais recente
                const lastDate = new Date(Math.max(...data.dates.map(date => new Date(date))));
                
                // Calcular data 10 anos atrás
                const tenYearsAgo = new Date(lastDate.getFullYear() - 10, lastDate.getMonth(), lastDate.getDate());
                
                // Filtrar dados
                const filteredData = data.dates.reduce((acc, date, index) => {
                    const currentDate = new Date(date);
                    if (currentDate >= tenYearsAgo) {
                        acc.dates.push(date);
                        acc.values.push(data.values[index]);
                    }
                    return acc;
                }, { dates: [], values: [] });

                filteredDates = filteredData.dates;
                filteredValues = filteredData.values;
            }

            // Formatar labels com trimestre
            // const formattedLabels = formatChartLabels(data.dates, 'trimester');
            
            const formattedLabels = formatChartLabels(filteredDates, 'trimester');

            // Destruir gráfico existente, se houver
            if (window.desocupacaoPbChart instanceof Chart) {
                window.desocupacaoPbChart.destroy();
            }

            window.desocupacaoPbChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'Taxa de Desocupação da Paraíba (%)',
                        // data: data.values,
                        data: filteredValues,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Paraíba: Taxa de Desocupação'
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: ' '
                            },
                            // Configurações para ajuste dinâmico
                            ticks: {
                                autoSkip: true,
                                maxTicksLimit: 20  // Limite máximo de ticks
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '(%)'
                            },
                            beginAtZero: true
                        }
                    }
                }
            });

            console.log('Gráfico de Desocupação da Paraíba renderizado com sucesso');
        })
        .catch(error => {
            console.error('Erro ao buscar dados de Desocupação da Paraíba:', error);
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados de Desocupação da Paraíba: ${error.message}`;
            }
        });
}



/// Estou inserindo a lógica da data aqui

function fetchIpcaData(chartId = 'IpcaChartFull', endpoint = '/api/ipca', dynamicRange = true) {
    console.log(`Iniciando busca de dados do IPCA no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de IPCA encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados do IPCA disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do IPCA');
                return;
            }

            // Lógica para intervalo dinâmico
            let filteredDates = data.dates;
            let filteredValues = data.values;

            if (dynamicRange) {
                // Encontrar a data mais recente
                const lastDate = new Date(Math.max(...data.dates.map(date => new Date(date))));
                
                // Calcular data 10 anos atrás
                const tenYearsAgo = new Date(lastDate.getFullYear() - 10, lastDate.getMonth(), lastDate.getDate());
                
                // Filtrar dados
                const filteredData = data.dates.reduce((acc, date, index) => {
                    const currentDate = new Date(date);
                    if (currentDate >= tenYearsAgo) {
                        acc.dates.push(date);
                        acc.values.push(data.values[index]);
                    }
                    return acc;
                }, { dates: [], values: [] });

                filteredDates = filteredData.dates;
                filteredValues = filteredData.values;

                console.log(`🕰️ Dados filtrados de ${tenYearsAgo.toISOString().split('T')[0]} a ${lastDate.toISOString().split('T')[0]}`);
            }

            const formattedLabels = formatChartLabels(filteredDates, 'yearMonth');

            window.ipcaChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: data.label || 'IPCA',
                        data: filteredValues,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
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
                            text: 'Índice Nacional de Preços ao Consumidor Amplo (IPCA)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: data.unit || '%'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('❌ Erro ao buscar dados do IPCA:', error);
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados do IPCA: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}



// Função compartilhada para buscar dados da SELIC para montar o gráfico full

function fetchSelicData(chartId = 'SelicChartFull', endpoint = '/api/selic', dynamicRange = true) {
    console.log(`Iniciando busca de dados da SELIC no endpoint: ${endpoint}`);


    fetch(endpoint)
        .then(response => {
            console.log('Resposta para Selic:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de Selic recebidos:',{
                dates: data.dates,
                values: data.values,
                firstDate: data.dates[0],
                lastDate: data.dates[data.dates.length - 1],
                firstValue: data.values[0],
                lastValue: data.values[data.values.length - 1]
            });

                    
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

            // Lógica para intervalo dinâmico
            let filteredDates = data.dates;
            let filteredValues = data.values;

            if (dynamicRange) {
                // Encontrar a data mais recente
                const lastDate = new Date(Math.max(...data.dates.map(date => new Date(date))));
                
                // Calcular data 10 anos atrás
                const tenYearsAgo = new Date(lastDate.getFullYear() - 10, lastDate.getMonth(), lastDate.getDate());
                
                // Filtrar dados
                const filteredData = data.dates.reduce((acc, date, index) => {
                    const currentDate = new Date(date);
                    if (currentDate >= tenYearsAgo) {
                        acc.dates.push(date);
                        acc.values.push(data.values[index]);
                    }
                    return acc;
                }, { dates: [], values: [] });

                filteredDates = filteredData.dates;
                filteredValues = filteredData.values;

                console.log(`🕰️ Dados filtrados de ${tenYearsAgo.toISOString().split('T')[0]} a ${lastDate.toISOString().split('T')[0]}`);
            }

            // Fim da lógica para intervalo dinâmico

            // const formattedLabels = formatChartLabels(data.dates, 'monthly');
            const formattedLabels = formatChartLabels(filteredDates, 'yearMonth');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', filteredValues);

            window.selicChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: [{
                        label: 'SELIC',
                        data: filteredValues,
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
            console.log('🔍 Dados de Câmbio recebidos:', {
                dates: data.dates,
                values: data.values,
                firstDate: data.dates[0],
                lastDate: data.dates[data.dates.length - 1],
                firstValue: data.values[0],
                lastValue: data.values[data.values.length - 1]
            });
            
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
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado do BCPB encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados do BCPB disponíveis';
                return;
            }

            // Encontrar a data máxima
            const maxDate = new Date(Math.max(...data.dates.map(date => new Date(date))));
            
            // Calcular data de 10 anos atrás
            const tenYearsAgo = new Date(maxDate.getFullYear() - 20, maxDate.getDate());

            // Filtrar dados para os últimos 10 anos
            const filteredDates = [];
            const filteredValues = [];

            data.dates.forEach((date, index) => {
                const currentDate = new Date(date);
                if (currentDate >= tenYearsAgo) {
                    filteredDates.push(date);
                    filteredValues.push(data.values[index]);
                }
            });

            const ctx = document.getElementById(chartId).getContext('2d');
            
            // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do BCPB');
                return;
            }

            // Formatar labels mensais
            const formattedLabels = formatChartLabels(filteredDates, 'monthly');

            // Destruir gráfico existente, se houver
            if (window.bcpbChart instanceof Chart) {
                window.bcpbChart.destroy();
            }

            // Criar datasets com cores condicionais
            const datasets = [{
                label: 'BCPB',
                data: filteredValues,
                borderWidth: 2,
                tension: 0.1,
                // Usar uma função para definir a cor baseada no valor
                borderColor: filteredValues.map(value => value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)'),
                backgroundColor: filteredValues.map(value => value >= 0 ? 'rgba(135,206,250, 0.2)' : 'rgba(255,0,0, 0.2)'),
                segment: {
                    borderColor: ctx => {
                        const value = ctx.p0DataIndex !== undefined ? filteredValues[ctx.p0DataIndex] : 0;
                        return value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)';
                    }
                }
            }];

            window.bcpbChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: formattedLabels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: `Saldo da Balança Comercial da Paraíba (Últimos 10 anos)`
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Período'
                            },
                            ticks: {
                                autoSkip: true,
                                maxTicksLimit: 20,  // Limite máximo de ticks
                                callback: function(value, index, values) {
                                    // Mostrar apenas alguns labels para evitar poluição visual
                                    return index % 6 === 0 ? formattedLabels[value] : '';
                                }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Valor (R$)'
                            },
                            beginAtZero: true
                        }
                    }
                }
            });

            console.log('Gráfico do BCPB renderizado com sucesso');
        })
        .catch(error => {
            console.error('Erro ao buscar dados do BCPB:', error);
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados do BCPB: ${error.message}`;
            }
        });
}


// Função compartilhada para buscar dados do DIVPUB e montar o gráfico full

function fetchDivpubData(chartId = 'dividaPbChartFull', endpoint = '/api/divpub', dynamicRange = true) {
    console.log(`Iniciando busca de dados do DIVPUB no endpoint: ${endpoint}`);
    
    fetch(endpoint)
        .then(response => {
            console.log('Resposta para divpub:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Dados de divida recebidos:', data);
            
            // Verificar se há dados
            if (!data.dates || data.dates.length === 0) {
                console.error('Nenhum dado de divida encontrado');
                document.getElementById(chartId).innerHTML = 'Sem dados de divida disponíveis';
                return;
            }

            const ctx = document.getElementById(chartId).getContext('2d');
            
                        // Verificar se o contexto foi criado
            if (!ctx) {
                console.error('Não foi possível criar o contexto do gráfico do DIVPUB' );
                return;
            }


            // Lógica para intervalo dinâmico
            let filteredDates = data.dates;
            let filteredValues = data.values;

            if (dynamicRange) {
                // Encontrar a data mais recente
                const lastDate = new Date(Math.max(...data.dates.map(date => new Date(date))));
                
                // Calcular data 10 anos atrás
                const tenYearsAgo = new Date(lastDate.getFullYear() - 15, lastDate.getMonth(), lastDate.getDate());
                
                // Filtrar dados
                const filteredData = data.dates.reduce((acc, date, index) => {
                    const currentDate = new Date(date);
                    if (currentDate >= tenYearsAgo) {
                        acc.dates.push(date);
                        acc.values.push(data.values[index]);
                    }
                    return acc;
                }, { dates: [], values: [] });

                filteredDates = filteredData.dates;
                filteredValues = filteredData.values;

                console.log(`🕰️ Dados filtrados de ${tenYearsAgo.toISOString().split('T')[0]} a ${lastDate.toISOString().split('T')[0]}`);
            }


            //const formattedLabels = formatChartLabels(data.dates, 'monthly');
            const formattedLabels = formatChartLabels(filteredDates, 'yearMonth');

            console.log('Labels formatadas:', formattedLabels);
            console.log('Valores:', filteredValues);


             // Criar datasets com cores condicionais
             const datasets = [{
                label: 'DIVPUB',
                data: data.values,
                borderWidth: 2,
                tension: 0.1,
                // Usar uma função para definir a cor baseada no valor
                borderColor: data.values.map(value => value <= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)'),
                backgroundColor: data.values.map(value => value <= 0 ? 'rgba(135,206,250, 0.2)' : 'rgba(255,0,0, 0.2)'),
                segment: {
                    borderColor: ctx => {
                        const value = ctx.p0DataIndex !== undefined ? data.values[ctx.p0DataIndex] : 0;
                        return value >= 0 ? 'rgb(135,206,250)' : 'rgb(255,0,0)';
                    }
                }
            }];

            window.ipcaChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: formattedLabels,
                    datasets: datasets
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
                            text: 'Paraíba: Dívida Líquida do Governo'
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
            console.error('Erro completo ao buscar dados de DIVPUB');
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                chartElement.innerHTML = `Erro ao carregar dados de DIVPUB: ${error.message}`;
            } else {
                console.error('Elemento do gráfico não encontrado');
            }
        });
}
