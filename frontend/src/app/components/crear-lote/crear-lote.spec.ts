import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CrearLote } from './crear-lote';

describe('CrearLote', () => {
  let component: CrearLote;
  let fixture: ComponentFixture<CrearLote>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearLote],
    }).compileComponents();

    fixture = TestBed.createComponent(CrearLote);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
