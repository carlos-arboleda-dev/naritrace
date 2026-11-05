import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="landing-wrapper">
      <!-- Navbar -->
      <nav class="navbar navbar-expand-lg py-3 container">
        <a class="navbar-brand d-flex align-items-center fw-bold fs-4 text-success" href="#">
          <span class="me-2">🌱</span> NariTrace
        </a>
        <div class="collapse navbar-collapse justify-content-center">
          <ul class="navbar-nav gap-4">
            <li class="nav-item"><a class="nav-link text-dark" href="#">Cómo funciona</a></li>
            <li class="nav-item"><a class="nav-link text-dark" href="#">Para quién</a></li>
            <li class="nav-item"><a class="nav-link text-dark" href="#">Preguntas</a></li>
          </ul>
        </div>
        <div class="d-flex gap-3">
          <a routerLink="/login" class="btn btn-link text-dark text-decoration-none">Iniciar sesión</a>
          <a routerLink="/login" class="btn btn-success px-4 rounded-3">Crear cuenta</a>
        </div>
      </nav>

      <!-- Hero Section -->
      <div class="container mt-5 pt-4">
        <div class="row align-items-center">
          
          <!-- Texto Izquierda -->
          <div class="col-lg-6">
            <p class="text-success fw-bold small text-uppercase letter-spacing-1">
              <span class="me-2">🌱</span>TRAZABILIDAD CON RAÍCES COLOMBIANAS
            </p>
            <h1 class="display-3 fw-bold text-success mb-4" style="line-height: 1.1;">
              Cada lote tiene una historia. Hazla visible.
            </h1>
            <p class="fs-5 text-muted mb-4 pe-5">
              Conecta el origen, los procesos y el recorrido de tus productos. Del campo a quien los elige, en un solo QR.
            </p>
            
            <div class="d-flex gap-3 mb-4">
              <a routerLink="/registro" class="btn btn-success btn-lg px-4 py-3 rounded-3">Registrar mi primer lote &rarr;</a>
              <a routerLink="/trazabilidad/NT-2026-1F61BE" class="btn btn-outline-success btn-lg px-4 py-3 rounded-3">Ver una trazabilidad</a>
            </div>
            
            <p class="text-muted small">Sin tarjeta de crédito · Tu información, bajo tu control</p>
            
            <div class="d-flex align-items-center mt-5 pt-3">
              <div class="bg-success bg-opacity-25 p-3 rounded-3 me-3">
                <span class="fs-4">📍</span>
              </div>
              <div>
                <h6 class="fw-bold mb-1">Diseñado para el campo de Nariño</h6>
                <p class="text-muted small mb-0">Café, cacao, frutas y producción pecuaria</p>
              </div>
            </div>
          </div>

          <!-- Imagen Derecha -->
          <div class="col-lg-6 position-relative mt-5 mt-lg-0">
            <!-- Imagen simulada (puedes cambiarla por una real después) -->
            <img src="https://images.unsplash.com/photo-1611162458324-aae1eb4129a4?q=80&w=1000" 
                 alt="Caficultora en Nariño" 
                 class="img-fluid rounded-4 shadow-lg object-fit-cover" 
                 style="height: 550px; width: 100%;">
            
            <!-- Tarjeta flotante -->
            <div class="card position-absolute bottom-0 start-0 m-4 shadow-lg border-0 rounded-4" style="width: 85%;">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <small class="text-success fw-bold text-uppercase">Del campo a tu mesa</small>
                  <span class="badge bg-success bg-opacity-25 text-success rounded-pill px-3 py-2">Lote de ejemplo</span>
                </div>
                <h4 class="fw-bold mb-3">Café de origen · El Mirador</h4>
                <p class="text-muted small mb-0 d-flex align-items-center">
                  <span class="me-2">📍</span> Buesaco, Nariño · NT-260918-001 &nearr;
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Franja Verde Inferior -->
      <div class="footer-banner mt-5 py-5 text-white">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-md-4 mb-4 mb-md-0">
              <h5 class="fw-bold">Un origen claro. Una cadena mejor conectada.</h5>
            </div>
            <div class="col-md-8 d-flex justify-content-around text-center fw-bold">
              <div><span class="fs-5 me-2">🌱</span> Productores</div>
              <div><span class="fs-5 me-2">🏢</span> Centros de acopio</div>
              <div><span class="fs-5 me-2">🚚</span> Distribuidores</div>
              <div><span class="fs-5 me-2">🛒</span> Consumidores</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .landing-wrapper {
      background-color: #F8F6F0; /* Color beige del diseño */
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .letter-spacing-1 {
      letter-spacing: 1px;
    }
    .footer-banner {
      background-color: #0E3B2E; /* Verde oscuro profundo */
      margin-top: auto;
    }
    /* Ajustes responsivos para la tarjeta flotante */
    @media (max-width: 768px) {
      .card.position-absolute {
        position: relative !important;
        width: 100% !important;
        margin: 1rem 0 0 0 !important;
      }
    }
  `]
})
export class LandingComponent {
  codigoBusqueda: string = '';

  constructor(private router: Router) {}

  buscarLote() {
    if (this.codigoBusqueda.trim()) {
      this.router.navigate(['/trazabilidad', this.codigoBusqueda.trim()]);
    }
  }
}