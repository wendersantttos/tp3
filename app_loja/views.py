from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash
from .models import Produto, Pedido
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomPasswordChangeForm, PedidoForm
from django.db.models import Q, F

# Create your views here.

def home(request):
    return render(request,'home.html')

def produtos(request):

    termo_pesquisa = request.GET.get('q')

    if termo_pesquisa:
        # Se houver um termo de pesquisa, filtre os produtos por nome
        lista_de_produtos = Produto.objects.filter(Q(nome__icontains=termo_pesquisa))
    else:
        lista_de_produtos = Produto.objects.all()
    return render(request, 'produtos.html', {'lista_de_produtos': lista_de_produtos})

def contato(request):
    return render(request, 'contato.html')

def quemsomos(request):
    return render(request, 'quemsomos.html')

def queropedir(request):
    return render(request, 'queropedir.html')

def pedidos(request):

    lista_de_pedidos = Pedido.objects.filter(user=request.user).order_by(F('id').desc(nulls_last=True))

    return render(request, 'pedidos.html', {'lista_de_pedidos': lista_de_pedidos})


def excluir_pedido(request, pedido_id):
    
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        # Realize a lógica de exclusão aqui, por exemplo:
        pedido.delete()

        # Redirecione para a página de pedidos após a exclusão
        return redirect('pedidos')

def perfil(request):
    return render(request,'perfil.html')


@login_required
def alterarsenha(request):
    erro = None

    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            # Não chame form.save() diretamente, pois isso não salva no banco de dados
            user = form.save(commit=False)
            user.save()  # Agora salve explicitamente o usuário no banco de dados

            # Atualize a sessão para evitar logout
            update_session_auth_hash(request, user)

            
            return redirect('perfil')
            
        else:
            messages.success(request, 'Por favor, corrija os erros abaixo:')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'alterarsenha.html', {'form': form, 'erro': erro})


def cadastro(request):
   

    if request.method == "POST":
        username = request.POST.get('username')
        nome = request.POST.get('name')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmacao_senha = request.POST.get('senha2')

        if senha != confirmacao_senha:
            messages.warning(request, 'As senhas não coincidem.')
            
        else:
            user = User.objects.filter(username=username).first()

            if user:
                messages.warning(request, 'Já existe um usuário com esse nome.')
                
            else:
                user = User.objects.create_user(username=username, email=email, password=senha)
                user.first_name = nome
                user.save()

                return redirect('home')  # Redirecione para a página desejada após o cadastro

    return render(request, 'cadastro.html')

def login_view(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username, password=senha)
        
        if user is not None:
            login(request, user)
            # Redirecione para a página desejada após o login
            return render(request,'home.html')
        else:
            messages.error(request, 'Usuário ou senha inválido')
           
    
    return render(request, 'login.html')

@login_required
def novopedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            # Lógica de salvamento manual
            segmento = form.cleaned_data['segmento']
            massa = form.cleaned_data['massa']
            recheio = form.cleaned_data['recheio']
            data_de_entrega = form.cleaned_data['data_de_entrega']
            detalhes = form.cleaned_data['detalhes']

            # Supondo que você já tenha um usuário logado, pode acessá-lo através de request.user
            usuario = request.user

            # Crie o objeto Pedido
            pedido = Pedido.objects.create(
                user=usuario,
                segmento=segmento,
                massa=massa,
                recheio=recheio,
                data_de_entrega=data_de_entrega,
                detalhes=detalhes
            )

            # Redirecione ou faça o que for necessário
            messages.success(request, 'Pedido realizado com sucesso!')
    else:
        form = PedidoForm()

    return render(request, 'novopedido.html', {'form': form})

