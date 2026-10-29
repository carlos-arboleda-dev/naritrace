import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TrazabilidadPublica } from './trazabilidad-publica';

describe('TrazabilidadPublica', () => {
  let component: TrazabilidadPublica;
  let fixture: ComponentFixture<TrazabilidadPublica>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TrazabilidadPublica],
    }).compileComponents();

    fixture = TestBed.createComponent(TrazabilidadPublica);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
