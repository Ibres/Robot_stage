# Robot_stage
Trabalho de simulação em ambiente stage-ros2
Dependências:

sudo apt update

sudo apt install \
build-essential \
cmake \
git \
python3-colcon-common-extensions \
ros-humble-desktop \
libfltk1.3-dev \
libpng-dev \
libjpeg-dev \
libltdl-dev
Criação do Workspace

Criar o workspace ROS2:

mkdir -p ~/robot_stage/src

cd ~/robot_stage
Clonagem dos Repositórios

Entrar no diretório src:

cd ~/robot_stage/src

Clonar o simulador Stage:

git clone https://github.com/rtv/Stage.git

Clonar a interface ROS2 para o Stage:

git clone https://github.com/tuw-robotics/stage_ros2.git
Compilação Correta dos Pacotes

Durante o desenvolvimento foi identificado que a ordem de compilação é importante.

O pacote stage_ros2 depende do pacote stage.

Portanto, a sequência correta é:

# 1. Compilar o pacote Stage

Retornar ao workspace:

cd ~/robot_stage

Compilar apenas o pacote Stage:

colcon build --packages-select stage
# 2. Carregar o Ambiente do Workspace

Após a compilação do Stage:

source install/setup.bash

Verificar se o arquivo de configuração foi instalado:

find install -name "stage-config.cmake"

Saída esperada:

install/stage/lib/cmake/Stage/stage-config.cmake
# 3. Compilar o pacote stage_ros2

Após carregar o ambiente:

colcon build --packages-select stage_ros2

Se o ambiente tiver sido carregado corretamente, a compilação será concluída sem erros.

Instalação do Pacote de Navegação

Entrar novamente no diretório src:

cd ~/robot_stage/src

Clonar este repositório

Retornar ao workspace:

cd ~/robot_stage

Compilar o pacote:

colcon build --packages-select robot_navigator

Atualizar o ambiente:

source install/setup.bash

Verificar se o executável foi registrado:

ros2 pkg executables robot_navigator

Saída esperada:

robot_navigator navigator
Execução da Simulação
# Terminal 1

Carregar o ambiente:

source /opt/ros/humble/setup.bash
source ~/robot_stage/install/setup.bash

Executar o Stage:

ros2 launch stage_ros2 stage.launch.py \
world:=new_cave \
enforce_prefixes:=false \
one_tf_tree:=true
# Terminal 2

Carregar o ambiente:

source /opt/ros/humble/setup.bash
source ~/robot_stage/install/setup.bash

Executar o nó de navegação:

ros2 run robot_navigator navigator

# Estado Atual do Projeto

Versão preliminar para entrega parcial.

Funcionalidades principais de integração e navegação implementadas e em fase de ajuste fino dos parâmetros de controle e desvio de obstáculos.
