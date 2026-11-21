import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { DashboardComponent } from './components/dashboard/dashboard';
import { ListaLotesComponent } from './components/lista-lotes/lista-lotes';
import { DetalleLoteComponent } from './components/detalle-lote/detalle-lote';
import { CrearLoteComponent } from './components/crear-lote/crear-lote';
import { TrazabilidadPublicaComponent } from './components/trazabilidad-publica/trazabilidad-publica';
import { ListaFincasComponent } from './components/lista-fincas/lista-fincas';
import { LandingComponent } from './components/landing/landing';
import { RegistroComponent } from './components/registro/registro';
import { CrearFincaComponent } from './components/crear-finca/crear-finca';
import { InicioComponent } from './components/inicio/inicio';
import { AdminSeccionComponent } from './components/admin-seccion/admin-seccion';
import { DistribuidorListaComponent } from './components/distribuidor-lista/distribuidor-lista';
import { rolGuard } from './guards/rol.guard';
import { ProximamenteComponent } from './components/proximamente/proximamente';


export const routes: Routes = [
  { path: '', redirectTo: 'landing', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'landing', component: LandingComponent },
  { path: 'registro', component: RegistroComponent },
  // RUTA PÚBLICA (El cliente escanea el QR y entra aquí)
  { path: 'trazabilidad/:codigo', component: TrazabilidadPublicaComponent }, 

  {
    path: 'dashboard',
    component: DashboardComponent,
    children: [
      { path: '', redirectTo: 'resumen', pathMatch: 'full' },
      // Inicio: cada rol ve su propio panel
      { path: 'resumen', component: InicioComponent },

      // Productor
      { path: 'lotes', component: ListaLotesComponent, canActivate: [rolGuard('productor')] },
      { path: 'lotes/nuevo', component: CrearLoteComponent, canActivate: [rolGuard('productor')] },
      { path: 'lotes/:id', component: DetalleLoteComponent, canActivate: [rolGuard('productor')] },
      { path: 'fincas', component: ListaFincasComponent, canActivate: [rolGuard('productor')] },
      { path: 'fincas/nueva', component: CrearFincaComponent, canActivate: [rolGuard('productor')] },
      { path: 'movimientos', component: ProximamenteComponent, data: { titulo: 'Movimientos' }, canActivate: [rolGuard('productor')] },
      { path: 'documentos', component: ProximamenteComponent, data: { titulo: 'Documentos' }, canActivate: [rolGuard('productor')] },

      // Administrador
      { path: 'admin/productores', component: AdminSeccionComponent, data: { vista: 'productores' }, canActivate: [rolGuard('administrador')] },
      { path: 'admin/lotes', component: AdminSeccionComponent, data: { vista: 'lotes' }, canActivate: [rolGuard('administrador')] },
      { path: 'admin/municipios', component: AdminSeccionComponent, data: { vista: 'municipios' }, canActivate: [rolGuard('administrador')] },
      { path: 'admin/auditoria', component: AdminSeccionComponent, data: { vista: 'auditoria' }, canActivate: [rolGuard('administrador')] },
      { path: 'admin/solicitudes', component: AdminSeccionComponent, data: { vista: 'solicitudes' }, canActivate: [rolGuard('administrador')] },

      // Distribuidor / acopiador / transportador
      { path: 'inventario', component: DistribuidorListaComponent, data: { modo: 'inventario' }, canActivate: [rolGuard('distribuidor')] },
      { path: 'historial', component: DistribuidorListaComponent, data: { modo: 'historial' }, canActivate: [rolGuard('distribuidor')] },
    ]
  },
  { path: '**', redirectTo: '' }
];

